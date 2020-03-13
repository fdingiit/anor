#!/usr/bin/python2
# encoding=utf8
import json
import random


class UserStopSignal(object):
    """
    Signal of use decided stopping
    """
    pass

    def __repr__(self):
        return '[USER STOP]'


class _Block(object):
    """
    Basic running block in Anor, current type of block are:
      - job
    """
    def __init__(self, name):
        """
        Constructor

        @param name: block name
        """
        self._name = name

    @property
    def name(self):
        return self._name


class _Job(_Block):
    """
    Main part of Anor
    """
    def __init__(self,
                 name,
                 handler,
                 args=None,
                 kwargs=None,
                 contain_result=False,
                 confirm=False):
        """
        Constructor

        @param name: job name
        @param handler: job function handler
        @param args: args of handler
        @param kwargs: kwargs of handler
        @param contain_result: is there any result of a job in args/kwargs?
        @param confirm: should this job be confirmed to run by user?
        """

        super(_Job, self).__init__(name)
        self._handler = handler
        self._args = args or list()
        self._kwargs = kwargs or dict()

        self._contain_result = contain_result
        self._confirm = confirm

    def _default_decider(self):
        """
        A default decider which let user decide whether to continue current job by command line input

        @return: True if user input is 'yes' else False
        """
        print '[-default decider] Job brief:'
        print self
        print '[-default decider] Continue? [yes/no]'
        return True if raw_input() == 'yes' else False

    def do(self):
        try:
            # stop if user decide to stop
            if self._confirm and not self._default_decider():
                return UserStopSignal()

            return self._handler(*self._args, **self._kwargs)
        except Exception as e:
            raise e

    @property
    def args(self):
        return self._args

    @args.setter
    def args(self, a):
        self._args = a

    @property
    def kwargs(self):
        return self._kwargs

    @kwargs.setter
    def kwargs(self, a):
        self._kwargs = a

    def contain_result(self):
        return self._contain_result

    def __repr__(self):
        return json.dumps(
            {
                'name': self.name,
                'args': self.args,
                'kwargs': self.kwargs
            },
            indent=4)


def _default_choicer(candidate, prompt, max_cnt, auto, filter_func):
    if len(candidate) == 0:
        print 'You have no choice...'
        return None

    print prompt or 'Your choices:'
    print '-------------------------------------------------------'
    for i in range(len(candidate)):
        print i + 1, '|', repr(candidate[i]).decode('unicode-escape')
    print '-------------------------------------------------------'

    handler = _auto_choicer_handler if auto else _default_choicer_handler

    result = handler(candidate, max_cnt, filter_func)

    print 'Your choices are:'
    for ele in result:
        print repr(ele).decode('unicode-escape')

    return result


def _default_choicer_handler(candidate, max_cnt, filter_func):
    while True:
        try:
            print 'Please make choice(s) by index: [1-%d] ' % len(candidate)
            print '(split by comma \',\' if more than one, input \'all\' to choose all of them)'
            inputs = raw_input()
            if inputs == 'all':
                return candidate

            index = [int(s) for s in inputs.split(',')]

            elements = list()
            for i in index:
                # check out of index error
                if i <= 0:
                    raise IndexError

                ele = candidate[i - 1]
                if filter_func and not filter_func(ele):
                    print 'Contains element which cannot be picked:', ele
                    raise RuntimeError

                elements.append(ele)

            if len(elements) > max_cnt:
                print 'Too many...'
                raise RuntimeError

            return elements
        except Exception as e:
            print '[ERR]', e


def _auto_choicer_handler(candidate, max_cnt, filter_func):
    sample = candidate[:] if filter_func is None else filter(
        filter_func, candidate[:])
    random.shuffle(sample)

    return sample[:max_cnt]


class _Result(object):
    """
    Place holder for result of a job
    """
    def __init__(self, name):
        """
        Constructor

        @param name: job name
        """
        self._name = name

    @property
    def name(self):
        return self._name


class Anor(object):
    """
    Anor, Devourer of Gods (Jobs)
    """
    def __init__(self, name='Anor', always_confirm=False):
        """
        Constructor

        @param name: nick name of Anor
        @param always_confirm: should every single job will be confirmed before starting to do
        """
        self._blocks = list()

        self._name = name
        self._always_confirm = always_confirm

        self._job_cnt = 0
        self._job_results = dict(
        )  # save every job's result in case any other job may need

    @staticmethod
    def result_of(name):
        """
        Representation for result of a specific job

        @param name: job name
        @return: place holder for specific job
        """
        return _Result(name)

    @staticmethod
    def _args_contains_results(args=None, kwargs=None):
        """
        Check out if any result in args/kwargs

        @param args: args which to check
        @param kwargs: kwargs which to check
        @return: True if there is else False
        """
        if isinstance(args, _Result) or isinstance(kwargs, _Result):
            return True
        if args is not None:
            for a in args:
                if isinstance(a, _Result):
                    return True
        if kwargs is not None:
            for (k, v) in kwargs.iteritems():
                if isinstance(v, _Result):
                    return True
        return False

    def next_job(self, name, handler, args=None, kwargs=None, confirm=False):
        """
        Form the next job to be done

        @param name: job name
        @param handler: job handler
        @param args: job args
        @param kwargs: job kwargs
        @param confirm: should be confirmed before starting?
        @return: Anor with the job
        """
        contain_result = self._args_contains_results(args, kwargs)
        self._blocks.append(
            _Job(name, handler, args, kwargs, contain_result,
                 self._always_confirm or confirm))
        self._job_cnt += 1
        return self

    def next_job_choice_from(self,
                             name='default_choicer',
                             candidate=None,
                             prompt=None,
                             auto=False,
                             filter_func=None,
                             max_cnt=2 ^ 32 - 1,
                             confirm=False):
        """
        A useful choice from job

        @param name: job name
        @param candidate: bloody lucky candidate, should be a list, set or tuple
        @param prompt: message shown to user before choosing
        @param auto: auto random choose?
        @param filter_func: filter function of choicer
        @param max_cnt: max chances to choose
        @param confirm: should be confirmed before starting?
        @return: Anor with the choice job
        """
        contain_result = self._args_contains_results(candidate)
        self._blocks.append(
            _Job(name,
                 _default_choicer,
                 kwargs={
                     'candidate': candidate,
                     'prompt': prompt,
                     'max_cnt': max_cnt,
                     'auto': auto,
                     'filter_func': filter_func,
                 },
                 contain_result=contain_result,
                 confirm=self._always_confirm or confirm))
        self._job_cnt += 1
        return self

    def _cook_args(self, job):
        """
        Cook raw args/kwargs which may contain result placeholder to prepared ready-to-use values

        @param job: job which need to eat args
        @return: nothing indeed
        """
        if job.contain_result():
            # args is a result, which is a list
            # eg:
            # anor.next_job('example', example, args=anor.result_of('another'))
            if isinstance(job.args, _Result) and isinstance(
                    self._job_results[job.args.name], list):
                job.args = self._job_results[job.args.name]
            # args is a list, which may contain result
            # eg:
            # anor.next_job('example', example, args=[1, 2, anor.result_of('another')])
            elif isinstance(job.args, list) or \
                    isinstance(job.args, tuple) or \
                    isinstance(job.args, set) and len(job.args):
                job.args = [
                    self._job_results[a.name] if isinstance(a, _Result) else a
                    for a in job.args
                ]

            # kwargs is a result, which is a dict
            # eg:
            # anor.next_job('example', example, kwargs=anor.result_of('another'))
            if isinstance(job.kwargs, _Result) and isinstance(
                    self._job_results[job.kwargs.name], dict):
                job.kwargs = self._job_results[job.kwargs.name]
            # kwargs is a dict, which may contain result
            # eg:
            # anor.next_job('example', example, kwargs={'a': 1, 'b': 2, 'c': anor.result_of('another')])
            elif isinstance(job.kwargs, dict) and len(job.kwargs):
                kwargs_cooked = dict()
                for (k, v) in job.kwargs.items():
                    kwargs_cooked[k] = self._job_results[v.name] if isinstance(
                        v, _Result) else v
                job.kwargs = kwargs_cooked

    def fire(self):
        """
        And God said, “Let there be fire,” and there was fire.

                                                    --- Genesis 1:3

        @return: job finale result
        """
        try:
            current_job_index = 0
            last_result = None

            for block in self._blocks:
                current_job_index += 1
                print '========================== [%d/%d] [%s] ==========================' % (
                    current_job_index, self._job_cnt, block.name)

                self._cook_args(block)
                last_result = block.do()
                self._job_results[block.name] = last_result

                if isinstance(last_result, UserStopSignal):
                    return UserStopSignal()

                print '========================== [%d/%d] [end] ==========================' % (
                    current_job_index, self._job_cnt)

            return last_result
        except Exception as e:
            raise e
