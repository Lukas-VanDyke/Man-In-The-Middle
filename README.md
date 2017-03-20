# Man-In-The-Middle
A man in the middle program that simply forwards and logs communications between a client and server.

How to run:

python3 assignment2.py *logoptions srcport address destport*

logoptions specifies how the server will log communication, either raw (plaintext), strip (only printable characters), hex (identical to "hexdump -c"), or autoN (N-byte chunks of data with printable characters displayed properly, others display as hex value).

srcport specifies the port the server will listen on.

address specifies the address the server will connect to.

destport specifies the destination port the server will connect to.
