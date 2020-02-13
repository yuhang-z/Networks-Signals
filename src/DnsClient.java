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
    private static int flag = 1;

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
                        flag = 2;
                        args = Arrays.copyOfRange(args, 1, args.length);
                        break label;

                    case "-ns":
                        flag = 3;
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

            System.out.println("timeout: " + timeout);
            System.out.println("max retries: " + maxRetries);
            System.out.println("port: " + port);
            System.out.println("flag: " + flag);

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
        System.out.println("server: " + server);
        String[] nameList = name.split("[.]");

        try{
            for (String partName: nameList) {
                int partNameLength = partName.length();
                if (partNameLength < 8) {
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

        socketData = socketData + "00";     // add "00" to indicate end

        // indicate which flag I'm using
        switch (flag) {
            case 1:
                socketData = socketData + "0001";
                break;
            case 2:
                socketData = socketData + "0002";
                break;
            case 3:
                socketData = socketData + "0003";
                break;
            default:
                break;
        }

        // QCLASS
        socketData = socketData + "0001";

        socketData = socketData.replaceAll("..", "$0 ").trim();
//        System.out.println(socketData);

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
        System.out.println("1-------------------------");
        InetAddress ipAddress = InetAddress.getByName(server);
        DatagramSocket clientSocket = new DatagramSocket();

        DatagramPacket sendPacket = new DatagramPacket(bsocketData, bsocketData.length, ipAddress, port);
        //Send datagram to server
        clientSocket.send(sendPacket);

        System.out.println("2-------------------------");


        byte[] receiveData = new byte[1024];
        DatagramPacket receivePacket =
                new DatagramPacket(receiveData, receiveData.length);

        System.out.println("3-------------------------");

        //TODO: output
        //Read datagram from server
        clientSocket.receive(receivePacket);
        System.out.println("4-------------------------");
        System.out.println("\n\nReceived: " + receivePacket.getLength() + " bytes");

        for (int i = 0; i < receivePacket.getLength(); i++) {
            System.out.print(" 0x" + String.format("%x", receiveData[i]) + " " );
        }
        System.out.println("\n");


        //TODO: copy & paste from Dns_Client
        DataInputStream din = new DataInputStream(new ByteArrayInputStream(receiveData));
        System.out.println("Transaction ID: 0x" + String.format("%x", din.readShort()));
        System.out.println("Flags: 0x" + String.format("%x", din.readShort()));
        System.out.println("Questions: 0x" + String.format("%x", din.readShort()));
        System.out.println("Answers RRs: 0x" + String.format("%x", din.readShort()));
        System.out.println("Authority RRs: 0x" + String.format("%x", din.readShort()));
        System.out.println("Additional RRs: 0x" + String.format("%x", din.readShort()));

        int recLen = 0;
        while ((recLen = din.readByte()) > 0) {
            byte[] record = new byte[recLen];

            for (int i = 0; i < recLen; i++) {
                record[i] = din.readByte();
            }

            System.out.println("Record: " + new String(record, "UTF-8"));
        }

        System.out.println("Record Type: 0x" + String.format("%x", din.readShort()));
        System.out.println("Class: 0x" + String.format("%x", din.readShort()));

        System.out.println("Field: 0x" + String.format("%x", din.readShort()));
        System.out.println("Type: 0x" + String.format("%x", din.readShort()));
        System.out.println("Class: 0x" + String.format("%x", din.readShort()));
        System.out.println("TTL: 0x" + String.format("%x", din.readInt()));

        short addrLen = din.readShort();
        System.out.println("Len: 0x" + String.format("%x", addrLen));

        System.out.print("Address: ");
        for (int i = 0; i < addrLen; i++ ) {
            System.out.print("" + String.format("%d", (din.readByte() & 0xFF)) + ".");
        }





//        String modifiedSentence =
//                new String(receivePacket.getData());
//        System.out.println("FROM SERVER:" + modifiedSentence);
        clientSocket.close();

    }
}
