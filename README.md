# networksProjectsCompiling
Argument Structure:
[-t timeout] [-r max-retries] [-p port] [-mx|-ns] @server name

Example:
java DnsClient -t 10 -r 2 -ns @8.8.8.8 mcgill.ca


• port (optional) is the UDP port number of the DNS server. Default value: 53.

• -mx or -ns flags (optional) indicate whether to send a MX (mail server) or NS (name server) query. At most one of these can be given, and if neither is given then the client should send a type A (IP address) query.

• server (required) is the IPv4 address of the DNS server, in a.b.c.d. format.


