from unittest import TestCase
from anor import Anor


def double(x):
    print 'doubling...'
    return 2 * x


def triple(x):
    print 'tripling...'
    return 3 * x


def multiple(a, b):
    print 'multipling...'
    return a * b


def count_down(previous):
    now = previous - 1
    print '[count_down] %d...' % now if now != 0 else 'cyka blyat!!!!!!!!!!!!!!!!!'
    return now


def choice(array):
    print 'select from '
    print array
    my_choice = array[int(raw_input()) - 1]
    print 'great! you selected: %d' % my_choice
    return array


def pop(choices):
    print 'select from '
    print choices
    my_choice = int(raw_input())
    print 'great! you selected: %d' % my_choice
    choices.discard(my_choice)
    return choices


class Test(TestCase):
    def test_math(self):
        anor = Anor(name='math')

        result = anor.next_job('double', double, args=(1,)). \
            next_job('triple', triple, args=(2,)). \
            next_job('multiple', multiple, args=(anor.result_of('double'), anor.result_of('triple'))).fire()

        print result
        self.assertEqual(1 * 2 * 2 * 3, result)

    def test_count_down(self):
        anor = Anor(name='count_down')

        for i in range(10, 0, -1):
            name = 'count_down_at_%d' % i
            anor.next_job(name, count_down, args=(i,))

        result = anor.fire()
        print result
        self.assertEqual(0, result)

    def test_choice(self):
        choices = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

        anor = Anor()

        for i in range(5):
            anor.next_job('make_choice', choice, kwargs={'array': choices})

        anor.fire()

    def test_pop(self):
        choices = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10}

        anor = Anor()

        current_name = ''
        last_name = ''
        for i in range(5):
            last_name = current_name
            current_name = 'pop_at_%d' % i
            anor.next_job(current_name, pop, kwargs={'choices': choices if i == 0 else anor.result_of(last_name)})

        print anor.fire()

    def test_always_decide(self):
        anor = Anor(name='decide', always_decide=True)

        result = anor. \
            next_job('double', double, args=(2,)). \
            next_job('triple', triple, args=(2,)). \
            next_job('multiple', multiple, args=(anor.result_of('double'), anor.result_of('triple'))). \
            fire()

        print result
        self.assertEqual(2 * 2 * 2 * 3, result)

    def test_specific_decide(self):
        anor = Anor(name='specific')

        result = anor. \
            next_job('double', double, args=(3,)). \
            next_job('triple', triple, args=(2,)). \
            next_job('multiple', multiple, args=(anor.result_of('double'), anor.result_of('triple')),
                     decide=True). \
            fire()

        print result
        self.assertEqual(3 * 2 * 2 * 3, result)