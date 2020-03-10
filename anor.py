#!/usr/bin/python2
# coding=utf8
import json


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


_default_choicer_name = 'default_choicer'


def _default_choicer_handler(candidate, prompt):
    print 'Your choices:' if prompt is None else prompt
    print '-------------------------------------------------------'
    for i in range(len(candidate)):
        print i + 1, '|', candidate[i]
    print '-------------------------------------------------------'

    if len(candidate) == 0:
        print 'You have no choice...'
        return None

    while True:
        print 'Please make choice by index: [1-%d] ' % len(candidate)
        print '(split by comma \',\' if more than one, \'all\' for choice all of them)'
        inputs = raw_input()
        if inputs == 'all':
            return candidate

        choices = [int(s) for s in inputs.split(',')]

        # check out of index error
        for choice in choices:
            try:
                if choice <= 0:
                    raise IndexError
                _ = candidate[choice - 1]
            except IndexError:
                print '[!ERR] Out of index: %d' % choice
                return None

        print 'Your choices are:'
        elements = [candidate[choice - 1] for choice in choices]
        for ele in elements:
            print ele
        return [candidate[choice - 1] for choice in choices]


class _ResultName(object):
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
        return _ResultName(name)

    @staticmethod
    def _args_contains_results(args=None, kwargs=None):
        """
        Check out if any result in args/kwargs

        @param args: args which to check
        @param kwargs: kwargs which to check
        @return: True if there is else False
        """
        if isinstance(args, _ResultName) or isinstance(kwargs, _ResultName):
            return True
        if args is not None:
            for a in args:
                if isinstance(a, _ResultName):
                    return True
        if kwargs is not None:
            for (k, v) in kwargs.iteritems():
                if isinstance(v, _ResultName):
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
                             name=_default_choicer_name,
                             candidate=None,
                             prompt=None,
                             confirm=False):
        """
        A useful choice from job

        @param name: job name
        @param candidate: bloody lucky candidate, should be a list, set or tuple
        @param confirm: should be confirmed before starting?
        @param prompt: message before choosing
        @return: Anor with the choice job
        """
        contain_result = self._args_contains_results(candidate)
        self._blocks.append(
            _Job(name,
                 _default_choicer_handler,
                 kwargs={
                     'candidate': candidate,
                     'prompt': prompt,
                 },
                 contain_result=contain_result,
                 confirm=self._always_confirm or confirm))
        self._job_cnt += 1
        return self

    def _prepare_args(self, job):
        """
        Cook the args which current job needs

        @param job: job which need to eat args
        @return: nothing indeed
        """
        if job.contain_result():
            # args is a result, result is a list
            # eg:
            # anor.next_job('example', example, args=anor.result_of('another'))
            if isinstance(job.args, _ResultName):
                if isinstance(self._job_results[job.args.name], list):
                    job.args = self._job_results[job.args.name]
            # args is a list, which may contain result
            # eg:
            # anor.next_job('example', example, args=[1, 2, anor.result_of('another')])
            elif isinstance(job.args, list) or \
                    isinstance(job.args, tuple) or \
                    isinstance(job.args, set) and len(job.args):
                job.args = [
                    self._job_results[a.name]
                    if isinstance(a, _ResultName) else a for a in job.args
                ]

            # kwargs is a result, result is a dict
            # eg:
            # anor.next_job('example', example, kwargs=anor.result_of('another'))
            if isinstance(job.kwargs, _ResultName):
                if isinstance(self._job_results[job.kwargs.name], dict):
                    job.kwargs = self._job_results[job.kwargs.name]
            # kwargs is a dict, which may contain result
            # eg:
            # anor.next_job('example', example, kwargs={'a': 1, 'b': 2, 'c': anor.result_of('another')])
            elif isinstance(job.kwargs, dict) and len(job.kwargs):
                kwargs_copy = dict()
                for (k, v) in job.kwargs.items():
                    if isinstance(v, _ResultName):
                        kwargs_copy[k] = self._job_results[v.name]
                    else:
                        kwargs_copy[k] = v
                job.kwargs = kwargs_copy

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

                self._prepare_args(block)
                last_result = block.do()
                self._job_results[block.name] = last_result

                if isinstance(last_result, UserStopSignal):
                    return UserStopSignal()

                print '========================== [%d/%d] [end] ==========================' % (
                    current_job_index, self._job_cnt)

            return last_result
        except Exception as e:
            raise e
