from __future__ import annotations

import datetime

import discord
from discord import MessageType
import pytest


client = discord.Client(intents=discord.Intents.all())


class MockCallMessage:
    def __init__(self, *, duration, participants, ended_timestamp):
        self.duration = duration
        self.participants = participants
        self.ended_timestamp = ended_timestamp


class MockMember:
    def __init__(self, *, id, name):
        self.id = id
        self.name = name


class MockMessage:
    def __init__(self, *, call):
        self.author = MockMember(id=1234, name='puncherdev')
        self.call = call
        self._state = client._connection
        self.type = MessageType.call

    def system_content(self) -> str:
        if self.type is MessageType.call:
            call_ended = self.call.ended_timestamp is not None  # type: ignore # call can't be None here
            missed = self._state.user not in self.call.participants  # type: ignore # call can't be None here

            if call_ended:
                seconds = self.call.duration.total_seconds()  # type: ignore # call can't be None here

                minutes_s = 60
                hours_s = minutes_s * 60
                days_s = hours_s * 24
                # Discord uses approx. 1/12 of 365.25 days (avg. days per year)
                months_s = days_s * 30.4375
                years_s = months_s * 12

                threshold_s = 45
                threshold_m = 45
                threshold_h = 21.5
                threshold_d = 25.5
                threshold_M = 10.5

                if seconds < threshold_s:
                    duration = "a few seconds"
                elif seconds < (threshold_m * minutes_s):
                    minutes = round(seconds / minutes_s)
                    if minutes == 1:
                        duration = "a minute"
                    else:
                        duration = f"{minutes} minutes"
                elif seconds < (threshold_h * hours_s):
                    hours = round(seconds / hours_s)
                    if hours == 1:
                        duration = "an hour"
                    else:
                        duration = f"{hours} hours"
                elif seconds < (threshold_d * days_s):
                    days = round(seconds / days_s)
                    if days == 1:
                        duration = "a day"
                    else:
                        duration = f"{days} days"
                elif seconds < (threshold_M * months_s):
                    months = round(seconds / months_s)
                    if months == 1:
                        duration = "a month"
                    else:
                        duration = f"{months} months"
                else:
                    years = round(seconds / years_s)
                    if years == 1:
                        duration = "a year"
                    else:
                        duration = f"{years} years"

                if missed:
                    return 'You missed a call from {0.author.name} that lasted {1}.'.format(self, duration)
                else:
                    return '{0.author.name} started a call that lasted {1}.'.format(self, duration)
            else:
                if missed:
                    return '{0.author.name} started a call. \N{EM DASH} Join the call'.format(self)
                else:
                    return '{0.author.name} started a call.'.format(self)

        # Fallback for unknown message types
        return ''


class Milliseconds:
    def __init__(self, years, months, days, hours, min, sec):
        self._years = years
        self._months = months
        self._days = days
        self._hours = hours
        self._min = min
        self._sec = sec

        self.value = (
            (years * 12 * 30.4375 * 24 * 60 * 60)
            + (months * 30.4375 * 24 * 60 * 60)
            + (days * 24 * 60 * 60)
            + (hours * 60 * 60)
            + (min * 60)
            + sec
        ) * 1000

    def __repr__(self):
        return f'<Milliseconds value={self.value} Y={self._years} M={self._months} D={self._days} h={self._hours} m={self._min} s={self._sec}>'


BASE_MISSED_ENDED = 'You missed a call from puncherdev that lasted {0}.'
BASE_NOT_MISSED_ENDED = 'puncherdev started a call that lasted {0}.'
NOT_MISSED_ONGOING = 'puncherdev started a call.'
MISSED_ONGOING = 'puncherdev started a call. \N{EM DASH} Join the call'

ENDED_TIMESTAMP = datetime.datetime(year=2024, month=2, day=20, hour=12, minute=45)


@pytest.mark.parametrize(
    ('milliseconds', 'participants', 'ended_timestamp', 'expected_output'),
    [
        #             Y  M  D  h  m  s
        (Milliseconds(0, 0, 0, 0, 0, 1), [], ENDED_TIMESTAMP, BASE_MISSED_ENDED.format('a few seconds')),
        (Milliseconds(0, 0, 0, 0, 0, 44), [], ENDED_TIMESTAMP, BASE_MISSED_ENDED.format('a few seconds')),
        (Milliseconds(0, 0, 0, 0, 0, 45), [], ENDED_TIMESTAMP, BASE_MISSED_ENDED.format('a minute')),
        (Milliseconds(0, 0, 0, 0, 1, 29), [], ENDED_TIMESTAMP, BASE_MISSED_ENDED.format('a minute')),
        (Milliseconds(0, 0, 0, 0, 1, 30), [], ENDED_TIMESTAMP, BASE_MISSED_ENDED.format('2 minutes')),
        (Milliseconds(0, 0, 0, 0, 44, 0), [], ENDED_TIMESTAMP, BASE_MISSED_ENDED.format('44 minutes')),
        (Milliseconds(0, 0, 0, 0, 45, 0), [], ENDED_TIMESTAMP, BASE_MISSED_ENDED.format('an hour')),
        (Milliseconds(0, 0, 0, 1, 29, 0), [], ENDED_TIMESTAMP, BASE_MISSED_ENDED.format('an hour')),
        (Milliseconds(0, 0, 0, 1, 30, 0), [], ENDED_TIMESTAMP, BASE_MISSED_ENDED.format('2 hours')),
        (Milliseconds(0, 0, 0, 21, 29, 0), [], ENDED_TIMESTAMP, BASE_MISSED_ENDED.format('21 hours')),
        (Milliseconds(0, 0, 0, 21, 30, 0), [], ENDED_TIMESTAMP, BASE_MISSED_ENDED.format('a day')),
        (Milliseconds(0, 0, 1, 11, 59, 0), [], ENDED_TIMESTAMP, BASE_MISSED_ENDED.format('a day')),
        (Milliseconds(0, 0, 1, 12, 0, 0), [], ENDED_TIMESTAMP, BASE_MISSED_ENDED.format('2 days')),
        (Milliseconds(0, 0, 25, 11, 0, 0), [], ENDED_TIMESTAMP, BASE_MISSED_ENDED.format('25 days')),
        (Milliseconds(0, 0, 25, 12, 0, 0), [], ENDED_TIMESTAMP, BASE_MISSED_ENDED.format('a month')),
        (Milliseconds(0, 1, 15, 5, 14, 0), [], ENDED_TIMESTAMP, BASE_MISSED_ENDED.format('a month')),
        (Milliseconds(0, 1, 15, 5, 15, 0), [], ENDED_TIMESTAMP, BASE_MISSED_ENDED.format('2 months')),
        (Milliseconds(0, 10, 15, 5, 14, 0), [], ENDED_TIMESTAMP, BASE_MISSED_ENDED.format('10 months')),
        (Milliseconds(0, 10, 15, 5, 15, 0), [], ENDED_TIMESTAMP, BASE_MISSED_ENDED.format('a year')),
        (Milliseconds(1, 5, 30, 0, 0, 0), [], ENDED_TIMESTAMP, BASE_MISSED_ENDED.format('a year')),
        (Milliseconds(1, 6, 0, 0, 0, 0), [], ENDED_TIMESTAMP, BASE_MISSED_ENDED.format('2 years')),
        (Milliseconds(10, 1, 0, 0, 0, 0), [], ENDED_TIMESTAMP, BASE_MISSED_ENDED.format('10 years')),
        (Milliseconds(10, 2, 0, 0, 0, 0), [client.user], ENDED_TIMESTAMP, BASE_NOT_MISSED_ENDED.format('10 years')),
        (Milliseconds(10, 3, 0, 0, 0, 0), [], None, MISSED_ONGOING),
        (Milliseconds(10, 4, 0, 0, 0, 0), [client.user], None, NOT_MISSED_ONGOING),
    ],
)
def test_call_system_content(milliseconds, participants, ended_timestamp, expected_output):
    duration = datetime.timedelta(milliseconds=milliseconds.value)

    call = MockCallMessage(duration=duration, participants=participants, ended_timestamp=ended_timestamp)
    message = MockMessage(call=call)

    assert message.system_content() == expected_output
