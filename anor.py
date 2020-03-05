#!/usr/bin/python2
# coding=utf8


class _StopSignal(object):
    pass


class _Block(object):
    def __init__(self, name):
        self._name = name

    @property
    def name(self):
        return self._name


class _Job(_Block):
    def __init__(self,
                 name,
                 handler,
                 args=None,
                 kwargs=None,
                 contain_result=False,
                 decide=False):

        super(_Job, self).__init__(name)
        self._handler = handler
        self._args = args or list()
        self._kwargs = kwargs or dict()

        self._contain_result = contain_result
        self._decide = decide

    def _default_decider(self):
        print '[-default decider] job brief:', self
        print '[-default decider] continue? [yes/no]'
        return True if raw_input() == 'yes' else False

    def do(self):
        try:
            if self._decide and not self._default_decider():
                return _StopSignal()
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
        return '{name: %s, args: %s, kwargs: %s}' % (self.name, self.args,
                                                     self.kwargs)


_default_decider_name = 'default_decider'


def _default_decider_handler(block):
    print '[-default decider] next block:', block
    print '[-default decider] continue? [yes/no]'
    return True if raw_input() == 'yes' else False


_default_choicer_name = 'default_choicer'


def _default_choicer_handler(*info):
    print 'Your choices:'
    print '-------------------------------------------------------'
    for i in range(len(info)):
        print i + 1, '|', info[i]
    print '-------------------------------------------------------'

    while True:
        print 'Please choice by index: [1-%d]' % len(info)
        choice = int(raw_input())
        if 1 <= choice <= len(info):
            print 'Your choice is:', choice
            print info[choice - 1]
            return info[choice - 1]


class _ResultName(object):
    def __init__(self, name):
        self._name = name

    @property
    def name(self):
        return self._name


class Anor(object):
    def __init__(self,
                 name='Anor',
                 args=None,
                 kwargs=None,
                 always_decide=False):
        self._blocks = list()

        self._name = name
        self._args = args
        self._kwargs = kwargs
        self._always_decide = always_decide

        self._job_cnt = 0
        self._job_results = dict(
        )  # save every job's result in case any other job may need

    @staticmethod
    def result_of(name):
        return _ResultName(name)

    @staticmethod
    def _args_contains_results(args=None, kwargs=None):
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

    def next_job(self, name, handler, args=None, kwargs=None, decide=False):
        contain_result = self._args_contains_results(args, kwargs)
        self._blocks.append(
            _Job(name, handler, args, kwargs, contain_result,
                 self._always_decide or decide))
        self._job_cnt += 1
        return self

    def next_job_choice_from(self,
                             name=_default_choicer_name,
                             args=None,
                             decide=False):
        contain_result = self._args_contains_results(args)
        self._blocks.append(
            _Job(name,
                 _default_choicer_handler,
                 args=args,
                 contain_result=contain_result,
                 decide=self._always_decide or decide))
        self._job_cnt += 1
        return self

    def _prepare_args(self, job):
        if job.contain_result():
            if isinstance(job.args, _ResultName):
                # result must be an array
                if isinstance(self._job_results[job.args.name], list):
                    job.args = [a for a in self._job_results[job.args.name]]
            if isinstance(job.args, list) or \
                    isinstance(job.args, tuple) or \
                    isinstance(job.args, set) and len(job.args):
                job.args = [
                    self._job_results[a.name]
                    if isinstance(a, _ResultName) else a for a in job.args
                ]
            if isinstance(job.kwargs, dict) and len(job.kwargs):
                kwargs_copy = dict()
                for (k, v) in job.kwargs.items():
                    if isinstance(v, _ResultName):
                        kwargs_copy[k] = self._job_results[v.name]
                    else:
                        kwargs_copy[k] = v
                job.kwargs = kwargs_copy

    def fire(self):
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

                if isinstance(last_result, _StopSignal):
                    print 'stop'
                    return

                print '========================== [%d/%d] [end] ==========================' % (
                    current_job_index, self._job_cnt)

            return last_result
        except Exception as e:
            raise e
