## Compile instruction for Assignemnt2:

### Argument Structure:
python fft.py [-m mode] [-i image]

[-m mode] : <br />
[1] (Default) for fast mode where the image is converted into its FFT form and displayed <br />
[2] for denoising where the image is denoised by applying an FFT, truncating high frequencies and then displayed <br />
[3] for compressing and saving the image<br />
[4] for plotting the runtime graphs for the report

[-i image] : <br />
filename of the image we wish to take the DFT of

### Compile Argument Example:
python3 fft.py 3 moonlanding.png

### Compile Notes:
• python 3.7 is recommanded <br />
• mode 3 is expected to take 5mins to complete <br />
• mode 4 is expected to take 1h complete <br />

### An exceptional discovery:
After comparing to the runtime of the **numpy 2dfft** function, we found our 2dfft algorithm is much slower in terms of runtime taken to complete, 
even though we implemented the it based on the **one dimension Cooley-Tukey FFT**. <br /> 
We are pleased to be informed if there are tricks to improve our algorithm runtime. Thanks for your time!<br /> 
