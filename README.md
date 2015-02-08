# ByteStream

This Python module provides a class called **ByteStream** that can be used to efficiently parse streams of byte data.
It uses the [memoryview](https://docs.python.org/3.4/library/stdtypes.html#memoryview) class to avoid copying blocks of memory any more than necessary so is pretty fast!

```python
>>> from bytestream import ByteStream
>>> stream = ByteStream()
>>> stream.write(b"abcdefg")
>>> stream.read(3).tobytes()
b"abc"
>>> stream.read(stream.available()).tobytes()
b"defg"
```
