import java.io.*;
import java.net.*;
import java.util.Arrays;
import java.util.Random;

public class DnsClient {
    // timeout (optional) gives how long to wait, in seconds, before retransmitting an unanswered query. Default value: 5.
    private static int timeout = 5;

    // max-retries (optional) is the maximum number of times to retransmit an unanswered query before giving up. Default value: 3.
    private static int maxRetries = 3;

    // port (optional) is the UDP port number of the DNS server. Default value: 53.
    private static int port = 53;

    //flags. Default value: 1
    // 1: A (IP address)
    // 2: MX (mail server)
    // 3: NS (name server)
    private static Type flag = Type.A;

    public static void main(String[] args) throws IOException {

        if(args.length < 2) {
            throw new IllegalArgumentException("ERROR \t Incorrect input: You must input both server and name!");
        }
        else {
            boolean timeoutflag = true;
            boolean maxretriesflag = true;
            boolean portflag = true;

            label:
            while (args.length > 2) {
                switch (args[0]) {
                    case "-t":
                        if (timeoutflag) {
                            timeoutflag = false;
                            try {
                                timeout = Integer.parseInt(args[1]);
                                if (timeout < 0) {
                                    throw new IllegalArgumentException("ERROR \t Incorrect input: Timeout cannot be negative!");
                                }
                            } catch (NumberFormatException e) {
                                throw new IllegalArgumentException("ERROR \t Incorrect input: Timeout is not valid!");
                            }
                        }
                        else {
                            throw new IllegalArgumentException("ERROR \t Incorrect input: Timeout has already been assigned!");
                        }
                        break;

                    case "-r":
                        if (maxretriesflag) {
                            maxretriesflag = false;
                            try {
                                maxRetries = Integer.parseInt(args[1]);
                                if (maxRetries < 0) {
                                    throw new IllegalArgumentException("ERROR \t Incorrect input: Max retries cannot be negative!");
                                }
                            } catch (NumberFormatException e) {
                                throw new IllegalArgumentException("ERROR \t Incorrect input: Max retries is not valid!");
                            }
                        }
                        else {
                            throw new IllegalArgumentException("ERROR \t Incorrect input: Max retries has already been assigned!");
                        }
                        break;

                    case "-p":
                        if (portflag) {
                            portflag = false;
                            try {
                                port = Integer.parseInt(args[1]);
                                if (port < 0) {
                                    throw new IllegalArgumentException("ERROR \t Incorrect input: Port cannot be negative!");
                                }
                            } catch (NumberFormatException e) {
                                throw new IllegalArgumentException("ERROR \t Incorrect input: Port is not valid!");
                            }
                        }
                        else {
                            throw new IllegalArgumentException("ERROR \t Incorrect input: Port has already been assigned!");
                        }
                        break;

                    case "-mx":
                        flag = Type.MX;
                        args = Arrays.copyOfRange(args, 1, args.length);
                        break label;

                    case "-ns":
                        flag = Type.NS;
                        args = Arrays.copyOfRange(args, 1, args.length);
                        break label;

                    default:
                        throw new IllegalArgumentException("ERROR \t Incorrect input: Wrong syntax!");
                }

                args = Arrays.copyOfRange(args, 2, args.length);
            }

            if (args.length != 2) {
                throw new IllegalArgumentException("ERROR \t Incorrect input: Wrong syntax!");
            }

        }


        String socketData = "";
        String server = args[0];
        String name = args[1];

        Random r = new Random();
        for (int a=0; a<4; a++) {
            int ID = r.nextInt(16);
            socketData = socketData + Integer.toHexString(ID);  // add the ID (random)
        }


        socketData = socketData + "01000001000000000000";


        server = server.substring(1);   // remove @
        String[] serverList = server.split("[.]");

        if(serverList.length != 4) {
            throw new IllegalArgumentException("ERROR \t Incorrect input: Server has to be valid!");
        }
        String[] nameList = name.split("[.]");

        try{
            for (String partName: nameList) {
                int partNameLength = partName.length();
                if (partNameLength < 16) {
                    socketData = socketData + "0" + Integer.toHexString(partNameLength);
                }
                else {
                    socketData = socketData + Integer.toHexString(partNameLength);
                }

                char[] partNameArr = partName.toCharArray();
                for (char ch: partNameArr) {
                    socketData = socketData + Integer.toHexString((int)ch);
                }

            }


        } catch (Exception e) {   //TODO: is it exception? More specific
            throw new IllegalArgumentException("ERROR \t Incorrect input: Both server and name have to be valid!");
        }


        System.out.println("DnsClient sending request for " + name);
        System.out.println("Server: " + server);
        switch (flag) {
            case A:
                System.out.println("Request type: A");
                break;
            case MX:
                System.out.println("Request type: MX");
                break;
            case NS:
                System.out.println("Request type: NS");
                break;
        }

        socketData = socketData + "00";     // add "00" to indicate end

        // indicate which flag I'm using
        switch (flag) {
            case A:
                socketData = socketData + "0001";
                break;
            case MX:
                socketData = socketData + "000f";
                break;
            case NS:
                socketData = socketData + "0002";
                break;
            default:
                break;
        }

        // QCLASS
        socketData = socketData + "0001";

        socketData = socketData.replaceAll("..", "$0 ").trim();
        //System.out.println(socketData);

        // convert socketData to byte array
        String[] socketDataList = socketData.split(" ");
        int z=0;
        byte[] bsocketData = new byte[socketDataList.length];
        for(String str: socketDataList) {
            int a = Character.digit(str.charAt(0), 16);
            int b = Character.digit(str.charAt(1), 16);
            bsocketData[z++] = (byte) ((a << 4) + b);
        }

//        for (int i =0; i< bsocketData.length; i++) {
//            System.out.print("0x" + String.format("%x", bsocketData[i]) + " " );
//        }

        //TODO: send query, socketdata is the input
        InetAddress ipAddress = InetAddress.getByName(server);
        DatagramSocket clientSocket = new DatagramSocket();
        clientSocket.setSoTimeout(timeout*1000);
        DatagramPacket sendPacket = new DatagramPacket(bsocketData, bsocketData.length, ipAddress, port);

        byte[] receiveData = new byte[1024];
        DatagramPacket receivePacket = new DatagramPacket(receiveData, receiveData.length);

        int retryNumber = 0;
        while (retryNumber < maxRetries) {
            try{

                long startTime = System.currentTimeMillis();
                //Send datagram to server
                clientSocket.send(sendPacket);

                // receive packet
                clientSocket.receive(receivePacket);

                long endTime = System.currentTimeMillis();
                clientSocket.close();

                System.out.println("Response received after " + (endTime - startTime)/1000. + " seconds");
                break;
            }
            //TODO: change the output
            catch (SocketException e) {
                System.out.println("ERROR\tCould not create socket");
            } catch (UnknownHostException e ) {
                System.out.println("ERROR\tUnknown host");
            } catch (SocketTimeoutException e) {
                System.out.println("ERROR\tSocket Timeout");
                System.out.println("Reattempting request......");
                retryNumber++;
                continue;
            } catch (Exception e) {
                System.out.println(e.getMessage());
            }
        }
        if (retryNumber == maxRetries) {
            throw new SocketException("ERROR \t Maximum number of retries " + maxRetries + " exceeded!");
        }



        DnsResponse response = new DnsResponse(receivePacket.getData(), bsocketData.length, flag);
        response.outputResponse();


























//        //Yuhang Zhang
//
//        System.out.println("\n\nReceived: " + receivePacket.getLength() + " bytes");
//
//        for (int i = 0; i < receivePacket.getLength(); i++) {
//            System.out.print(" 0x" + String.format("%x", receiveData[i]) + " " );
//        }
//        System.out.println("\n");
//
//
//
//        DataInputStream din = new DataInputStream(new ByteArrayInputStream(receiveData));
//
//        //COMMAND LINE OUTPUT ARGUMENTS:
//
//        //Authority
//        String auth = "";
//
//        //Return type
//        String rtype = "";
//
//        //TTL The number of seconds the results can be cached.
//        String numsec = "";
//
//
//        //Section1-----------------Name---------------- "only extract authority information"
//
//        //TransactionID--1
//        String returnID = String.format("%x", din.readShort());
//        String temp1 = String.format("%x", din.readShort());
//        String returnQR = temp1.substring(0, 1);
//
//        //System.out.println("Transaction ID: 0x" + );
//
//        //Flags----------2
//        din.readShort();
//        //System.out.println("Flags: 0x" + String.format("%x", din.readShort()));
//
//        //Questions------3
//        din.readShort();
//        //System.out.println("Questions: 0x" + String.format("%x", din.readShort()));
//
//        //OPCODE---------4
//        din.readShort();
//        //System.out.println("Answers RRs: 0x" + String.format("%x", din.readShort()));
//
//        //***Authority---5
//        auth = String.format("%x", din.readShort());
//        //System.out.println("Authority RRs: 0x" + String.format("%x", din.readShort()));
//        System.out.println(auth);
//
//        //TC-------------6
//        din.readShort();
//        //System.out.println("Additional RRs: 0x" + String.format("%x", din.readShort()));
//
//        int recLen = 0;
//        while ((recLen = din.readByte()) > 0) {
//            byte[] record = new byte[recLen];
//
//            for (int i = 0; i < recLen; i++) {
//                record[i] = din.readByte();
//            }
//
//            //System.out.println("Record: " + new String(record, "UTF-8"));
//        }
//        //Record Type----7
//        din.readShort();
//        //System.out.println("Record Type: 0x" + String.format("%x", din.readShort()));
//        //Class----------8
//        din.readShort();
//        //System.out.println("Class: 0x" + String.format("%x", din.readShort()));
//        //Field----------9
//        din.readShort();
//        //System.out.println("Field: 0x" + String.format("%x", din.readShort()));
//
//        //*****Type-----10
//        rtype = String.format("%x", din.readShort());
//        System.out.println(rtype);
//        //System.out.println("Type: 0x" + String.format("%x", din.readShort()));
//
//        //Class---------11
//        //"Specify the class of the data in the RDATA field. You should expect 0x0001 for this project, representing Internet addresses."
//        din.readShort();
//        //System.out.println("Class: 0x" + String.format("%x", din.readShort()));
//
//        //***TTL--------12
//        numsec = String.format("%x", din.readShort());
//        //System.out.println("TTL: 0x" + String.format("%x", din.readInt()));
//        System.out.println(numsec);
//
//        din.readShort();
//
//        //addrLen-------13      determine the length of RDATA
//        short addrLen = din.readShort();
//        System.out.println("Len: 0x" + String.format("%x", addrLen));
//
//        //Section of RDATA
//
//        //System.out.println(Integer.parseInt(String.valueOf("f")));
//
//        byte[] bytes = rtype.getBytes("US-ASCII");
//
//        int a = bytes[0];
//
//        a =Integer.parseInt(String.valueOf(rtype));
//
//        int b =Integer.parseInt(String.valueOf(auth));
//
//        //IP
//        if(a == 1){
//        	String ipaddr ="";
//            for (int i = 0; i < addrLen; i++ ) {
//            	ipaddr = ipaddr.concat(String.format("%d", (din.readByte() & 0xFF)) + ".");
//            }
//            String authmessage;
//            if(b == 0) {
//            	authmessage = "nonauth";
//            }else {
//            	authmessage = "auth";
//            }
//            System.out.print("IP "+ipaddr+" "+numsec+" "+authmessage);
//            clientSocket.close();
//
//        }
//
//        //NS
//        if(a == 6) {
//        	/*
//        	String ipaddr ="";
//
//            //System.out.println("Record: " + new String(record, "UTF-8"));
//        	for (int i = 0; i < addrLen; i++ ) {
//            	ipaddr = ipaddr.concat(String.format("%d", (din.readByte() & 0xFF)) + " ");
//            }
//        	System.out.println("NS");
//        	System.out.println(ipaddr);
//        	*/
//        	int rec = 0;
//        	while ((rec = din.readByte()) > 0) {
//                byte[] record = new byte[rec];
//
//                for (int i = 0; i < rec; i++) {
//                    record[i] = din.readByte();
//                }
//
//                System.out.println("Record: " + new String(record, "UTF-8"));
//            }
//        	clientSocket.close();
//        }
//
//        //MX
//        if(a == 2) {
//        	System.out.println("MX");
//        	clientSocket.close();
//        }
    }
}
