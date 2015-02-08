#!/usr/bin/env python
# -*- encoding: utf-8 -*-


import sys


if sys.version_info >= (3,):
    def _byte_match(view, position, value):
        return view[position] == value
else:
    def _byte_match(view, position, value):
        return view[position] == chr(value)


class ByteStream(object):

    def __init__(self):
        self._chunks = []
        self._num_chunks = 0
        self._last_chunk = self._num_chunks - 1
        self._chunk_pointer = 0
        self._byte_pointer = 0

    def available(self):
        if self._chunk_pointer < self._last_chunk:
            return (len(self._current_chunk()) - self._byte_pointer +
                    sum(len(self._chunks[c])
                        for c in range(self._chunk_pointer + 1, self._num_chunks)))
        elif self._chunk_pointer == self._last_chunk:
            return len(self._current_chunk()) - self._byte_pointer
        else:
            return 0

    def find(self, byte):
        current_chunk = self._current_chunk()
        if current_chunk is None:
            return None
        if self._chunk_pointer < self._last_chunk:
            self._combine_ahead()
            current_chunk = self._current_chunk()
        position = self._byte_pointer
        length = len(current_chunk)
        while position < length:
            if _byte_match(current_chunk, position, byte):
                return position - self._byte_pointer + 1
            position += 1
        return None

    def read(self, size):
        """ Read a specified number of bytes from the stream. If this many
        bytes are not available, None is returned and the read pointer is
        unaffected.

        :param size: the number of bytes to read
        :return: a memoryview of the bytes read or None if not enough bytes are available
        """
        current_chunk = self._current_chunk()
        if current_chunk is None:
            return None
        start_pointer = self._byte_pointer
        self._byte_pointer += size
        if self._byte_pointer < len(current_chunk):
            # Enough data left in the current chunk
            view = current_chunk[start_pointer:self._byte_pointer]
        elif self._byte_pointer == len(current_chunk):
            # Only just enough data left in the current chunk!
            view = current_chunk[start_pointer:self._byte_pointer]
            self._chunk_pointer += 1
            self._byte_pointer = 0
        else:
            # Not enough data left in the current chunk
            self._byte_pointer = start_pointer
            available = self.available()
            if available >= size:
                self._combine_ahead()
                view = self.read(size)
            else:
                view = None
        return view

    def write(self, data):
        """ Append data to the end of the stream.

        :param data: the bytes to be appended
        """
        if data:
            self._chunks.append(memoryview(data))
            self._num_chunks = len(self._chunks)
            self._last_chunk = self._num_chunks - 1

    def _combine_ahead(self):
        if self._chunk_pointer < self._last_chunk:
            combined = (self._current_chunk()[self._byte_pointer:].tobytes() +
                        b"".join(self._chunks[c].tobytes()
                                 for c in range(self._chunk_pointer + 1, self._num_chunks)))
            self._chunks = (self._chunks[:self._chunk_pointer] +
                            [self._current_chunk()[:self._byte_pointer], memoryview(combined)])
            self._num_chunks = len(self._chunks)
            self._last_chunk = self._num_chunks - 1
            self._chunk_pointer += 1
            self._byte_pointer = 0
        else:
            pass

    def _current_chunk(self):
        try:
            return self._chunks[self._chunk_pointer]
        except IndexError:
            return None
