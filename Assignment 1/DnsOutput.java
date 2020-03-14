	
public class DnsOutput {
	 private int timeToLive, rdLength, mxPreference;
	 private String name, domain;
	 private byte[] queryClass;
	 private Type queryType;
	 private boolean auth;
	 private int byteLength;
	 
	public DnsOutput(boolean auth){
		 this.auth = auth;
	 }

	 public void outputRecord() {
		 String authString;
        switch(this.queryType) {
            case A:
				authString = this.auth ? "auth" : "nonauth";
				System.out.println("IP\t" + this.domain + "\t" + this.timeToLive + "\t" + authString);
                break;
            case NS:
            	authString = this.auth ? "auth" : "nonauth";
				System.out.println("NS\t" + this.domain + "\t" + this.timeToLive + "\t" + authString);
                break;
            case MX:
				authString = this.auth ? "auth" : "nonauth";
				System.out.println("MX\t" + this.domain + "\t" + mxPreference + "\t" + this.timeToLive + "\t" + authString);
                break;
			case CNAME:
				authString = this.auth ? "auth" : "nonauth";
				System.out.println("CNAME\t" + this.domain + "\t" + this.timeToLive + "\t" + authString);
				break;
			default:
				break;
        }
	}
	
    public int getByteLength() {
		return byteLength;
	}
	
	public void setByteLength(int byteLength) {
		this.byteLength = byteLength;
	}

	public void setTimeToLive(int timeToLive) {
		this.timeToLive = timeToLive;
	}

	public void setRdLength(int rdLength) {
		this.rdLength = rdLength;
	}

	public void setMxPreference(int mxPreference) {
		this.mxPreference = mxPreference;
	}

	public void setName(String name) {
		this.name = name;
	}

	public void setDomain(String domain) {
		this.domain = domain;
	}

	public void setQueryClass(byte[] queryClass) {
		this.queryClass = queryClass;
	}

	public Type getQueryType() {
		return queryType;
	}

	public void setQueryType(Type queryType) {
		this.queryType = queryType;
	}
}
