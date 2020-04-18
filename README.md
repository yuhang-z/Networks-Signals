# DNSNetworks & ImageProcessing(FFT)

### Author: Yuhang Zhang and Charles Liu

## Compile instruction for Assignemnt1(DNSNetworks):

### Argument Structure:
[-t timeout] [-r max-retries] [-p port] [-mx|-ns] @server name

### Example:
java DnsClient -t 10 -r 5 -ns @8.8.8.8 mcgill.ca

### Notes:

• UDP port number is set to a default value 53.

• DNS server only supports IPv4 address.

• JDK version 1.8 is recommended 

## Compile instruction for Assignemnt2(ImageProcessing):

### Argument Structure:
python fft.py [-m mode] [-i image]

[-m mode] : <br />
[1] (Default) for fast mode where the image is converted into its FFT form and displayed <br />
[2] for denoising where the image is denoised by applying an FFT, truncating high frequencies and then displayed <br />
[3] for compressing and saving the image<br />
[4] for plotting the runtime graphs for the report

[-i image] : <br />
filename of the image we wish to take the DFT of

### Example:
python3 fft.py 3 moonlanding.png

### Notes:
• python 3.7 is recommanded
