import unittest
import curses

try:
    from unittest.mock import Mock
    from unittest.mock import patch
    from unittest.mock import call
except ImportError:
    from mock import Mock
    from mock import patch
    from mock import call

from cantools.subparsers.monitor import Monitor


class Args(object):

    def __init__(self, database):
        self.database = database
        self.encoding = None
        self.frame_id_mask = None
        self.no_strict = False
        self.single_line = False
        self.bit_rate = None
        self.bus_type = 'socketcan'
        self.channel = 'vcan0'


class StdScr(object):

    def __init__(self):
        self.getmaxyx = Mock(side_effect=[(30, 64)])
        self.nodelay = Mock()
        self.clear = Mock()
        self.addstr = Mock()
        self.refresh = Mock()
        self.getkey = Mock(return_value='q')


class CanToolsMonitorTest(unittest.TestCase):

    maxDiff = None

    def assert_called(self, mock, expected):
        self.assertEqual(mock.call_args_list, expected)

    @patch('can.Notifier')
    @patch('can.Bus')
    @patch('curses.color_pair')
    @patch('curses.is_term_resized')
    @patch('curses.init_pair')
    @patch('curses.curs_set')
    @patch('curses.use_default_colors')
    def test_immediate_quit(self,
                            use_default_colors,
                            curs_set,
                            init_pair,
                            is_term_resized,
                            color_pair,
                            bus,
                            notifier):
        # Prepare mocks.
        stdscr = StdScr()
        args = Args('tests/files/motohawk.dbc')
        color_pair.side_effect = ['green', 'cyan']
        is_term_resized.return_value = False

        # Run monitor.
        monitor = Monitor(stdscr, args)
        monitor.run()

        # Check mocks.
        self.assert_called(use_default_colors, [call()])
        self.assert_called(curs_set, [call(False)])
        self.assert_called(
            init_pair,
            [
                call(1, curses.COLOR_BLACK, curses.COLOR_GREEN),
                call(2, curses.COLOR_BLACK, curses.COLOR_CYAN)
            ])
        self.assert_called(color_pair, [call(1), call(2)])
        self.assert_called(bus, [call(bustype='socketcan', channel='vcan0')])
        notifier.assert_called_once()
        self.assert_called(
            stdscr.addstr,
            [
                call(0,
                     0,
                     'Received: 0, Discarded: 0, Errors: 0'),
                call(1,
                     0,
                     '   TIMESTAMP  MESSAGE                                           ',
                     'green'),
                call(29,
                     0,
                     'q: Quit, f: Filter, p: Play/Pause, r: Reset                     ',
                     'cyan')
            ])


if __name__ == '__main__':
    unittest.main()