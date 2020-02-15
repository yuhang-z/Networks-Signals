import javafx.util.Pair;

import java.net.InetAddress;
import java.net.UnknownHostException;
import java.nio.ByteBuffer;

public class DnsResponse {
	private byte[] response;
    private boolean AA;
    private int RCODE;
    private int ANCOUNT;
    private int ARCOUNT;
    private DnsOutput[] answerRecords;
    private DnsOutput[] additionalRecords;
    private boolean noRecords = false;

	public DnsResponse(byte[] response, int requestSize, Type type) {
		this.response = response;

        /*
        First we check if returned type matches the original type
         */
        int index = 12;

        while (this.response[index] != 0) {
            index++;
        }
        byte[] qType = {this.response[index + 1], this.response[index + 2]};

        if (this.getTypeFromByteArray(qType) != type) {
            throw new RuntimeException("ERROR\tResponse query type does not match request query type");
        }


        /*
        Now we analyze the header
         */
        //QR
        boolean QR = getBit(response[2], 7) == 1;

        //AA
        this.AA = getBit(response[2], 2) == 1;

        //RCODE
        this.RCODE = response[3] & 0x0F;

        //QDCount
        byte[] QDCount = { response[4], response[5] };
        ByteBuffer wrapped = ByteBuffer.wrap(QDCount);
        int QDCOUNT = wrapped.getShort();

        //ANCount
        byte[] ANCount = { response[6], response[7] };
        wrapped = ByteBuffer.wrap(ANCount);
        this.ANCOUNT = wrapped.getShort();

        //NSCount
        byte[] NSCount = { response[8], response[9] };
        wrapped = ByteBuffer.wrap(NSCount);
        int NSCOUNT = wrapped.getShort();

        //ARCount
        byte[] ARCount = { response[10], response[11] };
        wrapped = ByteBuffer.wrap(ARCount);
        this.ARCOUNT = wrapped.getShort();

        
        answerRecords = new DnsOutput[ANCOUNT];
        int offSet = requestSize;
        for(int i = 0; i < ANCOUNT; i ++){
        	answerRecords[i] = this.analyzeAnswer(offSet);
        	offSet += answerRecords[i].getByteLength();
        }
        
        //ns count even though we don't do anything
        for(int i = 0; i < NSCOUNT; i++){
        	offSet += analyzeAnswer(offSet).getByteLength();
        }
        
        additionalRecords = new DnsOutput[ARCOUNT];
        for(int i = 0; i < ARCOUNT; i++){
        	additionalRecords[i] = this.analyzeAnswer(offSet);
        	offSet += additionalRecords[i].getByteLength();
        }
        try {
            this.checkRCodeForErrors();
        } catch(RuntimeException e){
        	noRecords = true;
        }

        if (!QR) {
            throw new RuntimeException("ERROR\tInvalid response from server: Message is not a response");
        }
    }

    public void outputResponse() {
        System.out.println();
        if (this.ANCOUNT <= 0  || noRecords) {
            System.out.println("NOTFOUND");
            return;
        }

        System.out.println("***Answer Section (" + this.ANCOUNT + " answerRecords)***");
       
        for (DnsOutput record : answerRecords){
        	record.outputRecord();	
        }

        System.out.println();

        if (this.ARCOUNT > 0) {
            System.out.println("***Additional Section (" + this.ARCOUNT + " answerRecords)***");
            for (DnsOutput record : additionalRecords){
            	record.outputRecord();
            }
        }
    }

	
	private void checkRCodeForErrors() {
	    switch( this.RCODE) {
            case 0:
                //No error
                break;
            case 1:
                throw new RuntimeException("Format error: the name server was unable to interpret the query");
            case 2:
                throw new RuntimeException("Server failure: the name server was unable to process this query due to a problem with the name server");
            case 3:
                throw new RuntimeException();
            case 4:
                throw new RuntimeException("Not implemented: the name server does not support the requested kind of query");
            case 5:
                throw new RuntimeException("Refused: the name server refuses to perform the requested operation for policy reasons");
        }
    }


    private DnsOutput analyzeAnswer(int index){
    	DnsOutput result = new DnsOutput(this.AA);

        String domain;
        int countByte = index;

        Pair domainResult = getDomainFromIndex(countByte);
        countByte += (int) domainResult.getValue();
        domain = (String) domainResult.getKey();
        
        //Name
        result.setName(domain);

        //TYPE
        byte[] ans_type = new byte[2];
        ans_type[0] = response[countByte];
        ans_type[1] = response[countByte + 1];
        
        result.setQueryType(getTypeFromByteArray(ans_type));

        countByte += 2;
        //CLASS
        byte[] ans_class = new byte[2];
        ans_class[0] = response[countByte];
        ans_class[1] = response[countByte + 1];
        if (ans_class[0] != 0 && ans_class[1] != 1) {
            throw new RuntimeException(("ERROR\tThe class field in the response answer is not 1"));
        }
        result.setQueryClass(ans_class);

        countByte +=2;
        //TTL
        byte[] TTL = { response[countByte], response[countByte + 1], response[countByte + 2], response[countByte + 3] };
        ByteBuffer wrapped = ByteBuffer.wrap(TTL);
        result.setTimeToLive(wrapped.getInt());

        countByte +=4;
        //RDLength
        byte[] RDLength = { response[countByte], response[countByte + 1] };
        wrapped = ByteBuffer.wrap(RDLength);
        int rdLength = wrapped.getShort();
        result.setRdLength(rdLength);

        countByte +=2;
        switch (result.getQueryType()) {
            case A:
                result.setDomain(analyzeATypeRData(countByte));
                break;
            case NS:
                result.setDomain(analyzeNSTypeRData(countByte));
                break;
            case MX:
                result.setDomain(analyzeMXTypeRData(countByte, result));
                break;
            case CNAME:
                result.setDomain(analyzeCNAMETypeRDdata(countByte));
                break;
            case OTHER:
            	break;
        }
        result.setByteLength(countByte + rdLength - index);
        return result;
    }

    private String analyzeATypeRData(int countByte) {
        String address = "";
        byte[] byteAddress= { response[countByte], response[countByte + 1], response[countByte + 2], response[countByte + 3] };
        try {
            InetAddress inetaddress = InetAddress.getByAddress(byteAddress);
            address = inetaddress.toString().substring(1);
        } catch (UnknownHostException e) {
            e.printStackTrace();
        }
        return address;
        
    }

    private String analyzeNSTypeRData(int countByte) {
    	return (String) getDomainFromIndex(countByte).getKey();
    }

    private String analyzeMXTypeRData(int countByte, DnsOutput record) {
    	byte[] mxPreference= {this.response[countByte], this.response[countByte + 1]};
    	ByteBuffer buf = ByteBuffer.wrap(mxPreference);
    	record.setMxPreference(buf.getShort());
    	return (String) getDomainFromIndex(countByte + 2).getKey();
    }

    private String analyzeCNAMETypeRDdata(int countByte) {
    	return (String) getDomainFromIndex(countByte).getKey();
    }


    private Pair getDomainFromIndex(int index){
    	int wordSize = response[index];
    	StringBuilder domain = new StringBuilder();
    	boolean start = true;
    	int count = 0;
    	while(wordSize != 0){
			if (!start){
				domain.append(".");
			}
	    	if ((wordSize & 0xC0) == 0xC0) {
	    		byte[] offset = { (byte) (response[index] & 0x3F), response[index + 1] };
	            ByteBuffer wrapped = ByteBuffer.wrap(offset);
	            domain.append(getDomainFromIndex(wrapped.getShort()).getKey());
	            index += 2;
	            count +=2;
	            wordSize = 0;
	    	}else{
	    		domain.append(getWordFromIndex(index));
	    		index += wordSize + 1;
	    		count += wordSize + 1;
	    		wordSize = response[index];
	    	}
            start = false;
            
    	}

        return new Pair<>(domain.toString(), count);
    }
    private String getWordFromIndex(int index){
    	StringBuilder word = new StringBuilder();
    	int wordSize = response[index];
    	for(int i =0; i < wordSize; i++){
    		word.append((char) response[index + i + 1]);
		}
    	return word.toString();
    }

    private int getBit(byte b, int position) {
    	return (b >> position) & 1;
    }

    private Type getTypeFromByteArray(byte[] qType) {
        if (qType[0] == 0) {
            if (qType[1] == 1) {
                return Type.A;
            } else if (qType[1] == 2) {
                return Type.NS;
            } else if (qType[1] == 15) {
                return  Type.MX;
            } else if (qType[1] == 5) {
            	return Type.CNAME;
            }else {
            	return Type.OTHER;
//                throw new RuntimeException("ERROR\tUnrecognized query type in response");
            }
        } else {
        	return Type.OTHER;
//        	throw new RuntimeException("ERROR\tUnrecognized query type in response");
        }
    }
}
