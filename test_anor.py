import random
from unittest import TestCase

from anor import Anor


class _TestError(Exception):
    def __init__(self, msg):
        self._msg = msg

    def __repr__(self):
        return self._msg


def double(x):
    print 'doubling...'
    return 2 * x


def triple(x):
    print 'tripling...'
    return 3 * x


def multiple(a, b):
    print 'multipling...'
    return a * b


class TestAuto(TestCase):
    def test_fire(self):
        anor = Anor(name='math')

        result = anor.next_job('double', double, args=(1,)). \
            next_job('triple', triple, args=(2,)). \
            next_job('multiple', multiple, args=(anor.result_of('double'), anor.result_of('triple'))).fire()

        print result
        self.assertEqual(1 * 2 * 2 * 3, result)

    def test_yet_another_fire(self):
        def count_down(previous):
            now = previous - 1
            print '[count_down] %d...' % now if now != 0 else 'cyka blyat!!!!!!!!!!!!!!!!!'
            return now

        anor = Anor(name='count_down')

        for i in range(10, 0, -1):
            name = 'count_down_at_%d' % i
            anor.next_job(name, count_down, args=(i, ))

        result = anor.fire()
        print result
        self.assertEqual(0, result)

    def test_prepare_args(self):
        anor = Anor(name='decide')

        result = anor.next_job('double', double, args=(1,)). \
            next_job('triple', triple, args=(2,)). \
            next_job('glue', lambda x, y: {'a': x, 'b': y},
                     args=[anor.result_of('double'), anor.result_of('triple')]). \
            next_job('multiple', multiple, kwargs=anor.result_of('glue')).fire()

        print result
        self.assertEqual(1 * 2 * 2 * 3, result)

    def test_auto_choice(self):
        choices = [1, 2, 3, 4, 5]
        anor = Anor()

        anor.next_job_choice_from('make_choice', candidate=choices, auto=True)

        result = anor.fire()
        print result

        self.assertEqual(len(choices), len(result))

    def test_auto_choice_max(self):
        choices = [x for x in range(1, 400)]
        anor = Anor()

        max_cnt = random.randint(1, 400)
        anor.next_job_choice_from('make_choice',
                                  candidate=choices,
                                  auto=True,
                                  max_cnt=max_cnt)

        result = anor.fire()
        print result

        self.assertEqual(max_cnt, len(result))

    def test_auto_choice_with_filter(self):
        def fltr(n):
            return False if n in [1, 3, 5] else True

        choices = [1, 2, 3, 4, 5]
        anor = Anor()

        anor.next_job_choice_from('with_filter',
                                  candidate=choices,
                                  auto=True,
                                  filter_func=fltr)

        result = anor.fire()
        print result

        self.assertEqual(2, len(result))

    def test_raise_exception(self):
        def exception():
            raise _TestError('my exception')

        anor = Anor()

        try:
            anor.next_job('raise', exception).fire()
        except Exception as e:
            print repr(e)


class TestManual(TestCase):
    def test_choice_from_array(self):
        choices = [5, 4, 3, 2, 1]
        anor = Anor()

        anor.next_job_choice_from('make_choice',
                                  candidate=choices,
                                  prompt='Choice a number you like:')

        print anor.fire()

    def test_choice_from_result(self):
        def init_list():
            return ['apple', 'banana', 'grape', 'orange']

        anor = Anor(name='choice')

        result = anor.next_job('init', init_list). \
            next_job_choice_from('choice', candidate=anor.result_of('init')). \
            fire()
        print result

    def test_result_as_kwargs(self):
        def pop(candidate):
            print 'select from '
            print candidate
            my_choice = int(raw_input())
            print 'great! you selected: %d' % my_choice
            candidate.discard(my_choice)
            return candidate

        choices = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10}

        anor = Anor()

        current_name = ''
        last_name = ''
        for i in range(5):
            last_name = current_name
            current_name = 'pop_at_%d' % i
            anor.next_job(current_name,
                          pop,
                          kwargs={
                              'candidate':
                              choices if i == 0 else anor.result_of(last_name)
                          })

        print anor.fire()

    def test_always_confirm(self):
        anor = Anor(name='decide', always_confirm=True)

        result = anor. \
            next_job('double', double, args=(2,)). \
            next_job('triple', triple, args=(2,)). \
            next_job('multiple', multiple, args=(anor.result_of('double'), anor.result_of('triple'))). \
            fire()

        print result
        self.assertEqual(2 * 2 * 2 * 3, result)

    def test_specific_confirm(self):
        anor = Anor(name='specific')

        result = anor. \
            next_job('double', double, args=(3,)). \
            next_job('triple', triple, args=(2,)). \
            next_job('multiple', multiple, kwargs={'a': anor.result_of('double'), 'b': anor.result_of('triple')},
                     confirm=True). \
            fire()

        print result
        self.assertEqual(3 * 2 * 2 * 3, result)

    def test_choice_with_filter(self):
        def fltr(n):
            return False if n in [1, 3, 5] else True

        choices = [1, 2, 3, 4, 5]
        anor = Anor()

        anor.next_job_choice_from('with_filter',
                                  candidate=choices,
                                  filter_func=fltr)

        result = anor.fire()
        print result
