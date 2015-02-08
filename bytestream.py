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
        """ Return the number of bytes available to read.
        """
        if self._chunk_pointer < self._last_chunk:
            return (len(self._current_chunk()) - self._byte_pointer +
                    sum(len(self._chunks[c])
                        for c in range(self._chunk_pointer + 1, self._num_chunks)))
        elif self._chunk_pointer == self._last_chunk:
            return len(self._current_chunk()) - self._byte_pointer
        else:
            return 0

    def read(self, size):
        """ Read a specified number of bytes from the stream. If this many
        bytes are not available, None is returned and the read pointer is
        unaffected.

        Note that this method returns a memoryview object which will
        generally require conversion via the `tobytes` method.

        :param size: the number of bytes to read
        :return: a memoryview of the bytes read or None if not enough bytes are available
        """
        if not size:
            return None
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

    def until(self, byte):
        """ Find the number of bytes to read until the next occurrence
        of the byte value specified is consumed. If no such occurrence
        exists, None is returned.

        :param byte: the numeric value of the byte to search for
        :return: the number of bytes to read or None if not available
        """
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

    def write(self, data):
        """ Append data to the end of the stream.

        :param data: the bytes to be appended
        """
        if data:
            self._chunks.append(memoryview(data))
            self._num_chunks = len(self._chunks)
            self._last_chunk = self._num_chunks - 1

    def _combine_ahead(self):
        """ Combine all the chunks ahead of the current pointer position into
        a single chunk for ease of processing.
        """
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

    def _current_chunk(self):
        """ Return the current chunk, if available.
        """
        try:
            return self._chunks[self._chunk_pointer]
        except IndexError:
            return None
