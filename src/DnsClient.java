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

    public static void main(String[] args) {
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


        try{
            String server = args[0];
            String name = args[1];
            String socketData = "";

            Random r = new Random();
            for (int a=0; a<4; a++) {
                int ID = r.nextInt(16);
                socketData = socketData + Integer.toHexString(ID);  // add the ID (random)
            }


            socketData = socketData + "01000001000000000000";


            server = server.substring(1);   // remove @
            String[] serverList = server.split("[.]");

            if(serverList.length != 4) {
                throw new IllegalArgumentException("ERROR \t Incorrect input: Both server and name have to be valid!");
            }

            String[] nameList = name.split("[.]");

            for (String partName: nameList) {
                int partNameLength = partName.length();
                if (partNameLength <8) {
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
            System.out.println(socketData);

        } catch (Exception e) {   //TODO: is it exception? More specific
            throw new IllegalArgumentException("ERROR \t Incorrect input: Both server and name have to be valid!");
        }


        //TODO: send query, socketdata is the input

        //TODO: output

    }
}
