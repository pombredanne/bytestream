#!/usr/bin/env python
# -*- encoding: utf-8 -*-


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
    found = b.find(97)
    assert found == 1
    found = b.find(98)
    assert found == 2
    found = b.find(99)
    assert found == 3


def test_cannot_find_byte_not_written():
    b = ByteStream()
    b.write(b"abc")
    found = b.find(100)
    assert found is None


def test_cannot_find_anything_if_empty():
    b = ByteStream()
    found = b.find(97)
    assert found is None


def test_finding_only_next_matching_byte():
    b = ByteStream()
    b.write(b"abcabc")
    found = b.find(97)
    assert found == 1
    found = b.find(98)
    assert found == 2
    found = b.find(99)
    assert found == 3


def test_find_updates_after_read():
    b = ByteStream()
    b.write(b"abcbca")
    found = b.find(97)
    assert found == 1
    found = b.find(98)
    assert found == 2
    found = b.find(99)
    assert found == 3
    b.read(3)
    found = b.find(97)
    assert found == 3
    found = b.find(98)
    assert found == 1
    found = b.find(99)
    assert found == 2


def test_can_find_bytes_several_chunks_ahead():
    b = ByteStream()
    b.write(b"xxx")
    b.write(b"xxx")
    b.write(b"xxx")
    b.write(b"abc")
    found = b.find(97)
    assert found == 10
    found = b.find(98)
    assert found == 11
    found = b.find(99)
    assert found == 12
