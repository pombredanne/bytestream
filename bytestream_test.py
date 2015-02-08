#!/usr/bin/env python
# -*- encoding: utf-8 -*-

# Copyright 2015, Nigel Small
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from bytestream import ByteStream


def test_can_write_then_read_simple_stream():
    b = ByteStream()
    b.write(b"hello")
    read = b.read(5)
    assert read.tobytes() == b"hello"


def test_can_write_two_then_read_as_one():
    b = ByteStream()
    b.write(b"hello,")
    b.write(b" world")
    read = b.read(12)
    assert read.tobytes() == b"hello, world"


def test_can_write_several_then_read_across_boundaries():
    b = ByteStream()
    b.write(b"aaa")
    b.write(b"bbb")
    b.write(b"ccc")
    b.write(b"ddd")
    read = b.read(4)
    assert read.tobytes() == b"aaab"
    read = b.read(4)
    assert read.tobytes() == b"bbcc"
    read = b.read(4)
    assert read.tobytes() == b"cddd"


def test_can_write_one_then_read_as_two():
    b = ByteStream()
    b.write(b"hello, world")
    read = b.read(6)
    assert read.tobytes() == b"hello,"
    read = b.read(6)
    assert read.tobytes() == b" world"


def test_read_returns_none_if_nothing_available():
    b = ByteStream()
    read = b.read(1)
    assert read is None


def test_read_returns_none_if_nothing_more_available():
    b = ByteStream()
    b.write(b"hello")
    b.read(5)
    read = b.read(1)
    assert read is None


def test_read_returns_none_if_not_enough_available():
    b = ByteStream()
    b.write(b"hello")
    read = b.read(10)
    assert read is None


def test_can_resume_reading_after_nothing_available():
    b = ByteStream()
    b.write(b"hello")
    b.read(5)
    read = b.read(1)
    assert read is None
    b.write(b"world")
    read = b.read(5)
    assert read.tobytes() == b"world"


def test_reading_nothing_does_nothing():
    b = ByteStream()
    b.write(b"hello")
    assert b.available() == 5
    b.read(0)
    assert b.available() == 5


def test_can_measure_how_much_available():
    b = ByteStream()
    assert b.available() == 0
    b.write(b"hello")
    assert b.available() == 5
    b.read(2)
    assert b.available() == 3
    b.read(2)
    assert b.available() == 1
    b.read(2)
    assert b.available() == 1
    b.read(1)
    assert b.available() == 0


def test_can_find_bytes():
    b = ByteStream()
    b.write(b"abc")
    distance = b.until(97)
    assert distance == 1
    distance = b.until(98)
    assert distance == 2
    distance = b.until(99)
    assert distance == 3


def test_cannot_find_byte_not_written():
    b = ByteStream()
    b.write(b"abc")
    distance = b.until(100)
    assert distance is None


def test_cannot_find_anything_if_empty():
    b = ByteStream()
    distance = b.until(97)
    assert distance is None


def test_distance_only_measured_to_next_matching_byte():
    b = ByteStream()
    b.write(b"abcabc")
    distance = b.until(97)
    assert distance == 1
    distance = b.until(98)
    assert distance == 2
    distance = b.until(99)
    assert distance == 3


def test_distance_changes_after_read():
    b = ByteStream()
    b.write(b"abcbca")
    distance = b.until(97)
    assert distance == 1
    distance = b.until(98)
    assert distance == 2
    distance = b.until(99)
    assert distance == 3
    b.read(3)
    distance = b.until(97)
    assert distance == 3
    distance = b.until(98)
    assert distance == 1
    distance = b.until(99)
    assert distance == 2


def test_can_find_bytes_several_chunks_ahead():
    b = ByteStream()
    b.write(b"xxx")
    b.write(b"xxx")
    b.write(b"xxx")
    b.write(b"abc")
    distance = b.until(97)
    assert distance == 10
    distance = b.until(98)
    assert distance == 11
    distance = b.until(99)
    assert distance == 12
