# -*- coding: utf-8 -*-

import six
import math
import functools


number_types = six.integer_types + (float, )


@functools.total_ordering
@six.python_2_unicode_compatible
class Angle(object):
    @classmethod
    def from_radians(cls, rad):
        return cls(math.degrees(rad))

    def __init__(self, degrees):
        self._degrees = float(degrees) % 360

    def __repr__(self):
        return 'Angle({!r})'.format(self._degrees)

    def __str__(self):
        return u'{:.1f}°'.format(self._degrees)

    def sin(self):
        return math.sin(self.radians)

    def cos(self):
        return math.cos(self.radians)

    @property
    def degrees(self):
        return self._degrees

    @property
    def radians(self):
        return math.radians(self._degrees)

    def __bool__(self):
        return bool(self._degrees)

    __nonzero__ = __bool__

    def __float__(self):
        return self._degrees

    def __add__(self, other):
        if not isinstance(other, Angle):
            return NotImplemented
        return Angle(self._degrees + other.degrees)

    def __sub__(self, other):
        if not isinstance(other, Angle):
            return NotImplemented
        return Angle(self._degrees - other.degrees)

    def __rmul__(self, other):
        return self.__mul__(other)

    def __mul__(self, other):
        if not isinstance(other, number_types):
            return NotImplemented
        return Angle(self._degrees * other)

    def __div__(self, other):
        if not isinstance(other, number_types):
            return NotImplemented
        return Angle(self._degrees / other)

    def __eq__(self, other):
        return isinstance(other, Angle) and other.degrees == self._degrees

    def __lt__(self, other):
        if not isinstance(other, Angle):
            return NotImplemented
        return self._degrees < other.degrees
