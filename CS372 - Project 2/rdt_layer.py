from segment import Segment


# #################################################################################################################### #
# RDTLayer                                                                                                             #
#                                                                                                                      #
# Description:                                                                                                         #
# The reliable data transfer (RDT) layer is used as a communication layer to resolve issues over an unreliable         #
# channel.                                                                                                             #
#                                                                                                                      #
#                                                                                                                      #
# Notes:                                                                                                               #
# This file is meant to be changed.                                                                                    #
#                                                                                                                      #
#                                                                                                                      #
# #################################################################################################################### #


class RDTLayer(object):
    # ################################################################################################################ #
    # Class Scope Variables                                                                                            #
    #                                                                                                                  #
    #                                                                                                                  #
    #                                                                                                                  #
    #                                                                                                                  #
    #                                                                                                                  #
    # ################################################################################################################ #
    DATA_LENGTH = 4  # in characters                     # The length of the string data that will be sent per packet...
    FLOW_CONTROL_WIN_SIZE = 15  # in characters          # Receive window size for flow-control
    sendChannel = None
    receiveChannel = None
    dataToSend = ''
    currentIteration = 0  # Use this for segment 'timeouts'

    # Add items as needed

    # ################################################################################################################ #
    # __init__()                                                                                                       #
    #                                                                                                                  #
    #                                                                                                                  #
    #                                                                                                                  #
    #                                                                                                                  #
    #                                                                                                                  #
    # ################################################################################################################ #
    def __init__(self):
        self.sendChannel = None
        self.receiveChannel = None
        self.dataToSend = ''
        self.currentIteration = 0
        self.dataReceived = ''
        self.sentDataList = []
        self.dataReceivedList = []
        self.counter = 0
        self.acknum = 0
        self.ackClient = 0
        self.segSent = 0
        self.countSegmentTimeouts = 0
        self.receivedSegments = {}
        self.sendingLimit = 0
        self.processAck = False
        self.savedSeqNum = []
        self.serverRunsCounter = 0
        self.clientAckLog = {}
        self.sentLog = {}
        self.timeLimit = 0
        # Add items as needed

    # ################################################################################################################ #
    # setSendChannel()                                                                                                 #
    #                                                                                                                  #
    # Description:                                                                                                     #
    # Called by main to set the unreliable sending lower-layer channel                                                 #
    #                                                                                                                  #
    #                                                                                                                  #
    # ################################################################################################################ #
    def setSendChannel(self, channel):
        self.sendChannel = channel

    # ################################################################################################################ #
    # setReceiveChannel()                                                                                              #
    #                                                                                                                  #
    # Description:                                                                                                     #
    # Called by main to set the unreliable receiving lower-layer channel                                               #
    #                                                                                                                  #
    #                                                                                                                  #
    # ################################################################################################################ #
    def setReceiveChannel(self, channel):
        self.receiveChannel = channel

    # ################################################################################################################ #
    # setDataToSend()                                                                                                  #
    #                                                                                                                  #
    # Description:                                                                                                     #
    # Called by main to set the string data to send                                                                    #
    #                                                                                                                  #
    #                                                                                                                  #
    # ################################################################################################################ #
    def setDataToSend(self, data):
        self.dataToSend = data

    # ################################################################################################################ #
    # getDataReceived()                                                                                                #
    #                                                                                                                  #
    # Description:                                                                                                     #
    # Called by main to get the currently received and buffered string data, in order                                  #
    #                                                                                                                  #
    #                                                                                                                  #
    # ################################################################################################################ #
    def getDataReceived(self):
        # ############################################################################################################ #
        # Identify the data that has been received...
        # ############################################################################################################ #


        return self.dataReceived

    # ################################################################################################################ #
    # processData()                                                                                                    #
    #                                                                                                                  #
    # Description:                                                                                                     #
    # "timeslice". Called by main once per iteration                                                                   #
    #                                                                                                                  #
    #                                                                                                                  #
    # ################################################################################################################ #
    def processData(self):
        self.currentIteration += 1
        self.processSend()
        self.processReceiveAndSendRespond()

    # ################################################################################################################ #
    # processSend()                                                                                                    #
    #                                                                                                                  #
    # Description:                                                                                                     #
    # Manages Segment sending tasks                                                                                    #
    #                                                                                                                  #
    #                                                                                                                  #
    # ################################################################################################################ #
    def processSend(self):
        segmentSend = Segment()
        # ############################################################################################################ #

        # You should pipeline segments to fit the flow-control window
        # The flow-control window is the constant RDTLayer.FLOW_CONTROL_WIN_SIZE
        # The maximum data that you can send in a segment is RDTLayer.DATA_LENGTH
        # These constants are given in # characters
        # Somewhere in here you will be creating data segments to send.
        # The data is just part of the entire string that you are trying to send.
        # The seqnum is the sequence number for the segment (in character number, not bytes)

        n = self.DATA_LENGTH
        # calculate how many packages can be sent at once by dividing flow control (amt of characters able to be sent w/o ack) by data length (max characters per packet)
        m = self.FLOW_CONTROL_WIN_SIZE // self.DATA_LENGTH

        missing = False
        currentAck = 0
        missingSegmentAck = 0
        droppedAck = False
        dropped_retransmission = False
        resend_packets = False

        if self.currentIteration >= self.timeLimit + 5:
            resend_packets = True

        if self.currentIteration == 1:
            createSegment = [self.dataToSend[i:i + n] for i in range(0, len(self.dataToSend), n)]
            for i in range(len(createSegment)):
                self.sentLog[i] = createSegment[i]

        if self.processAck:
            incomingAck = self.receiveChannel.receive()
            if not incomingAck:
                droppedAck = True
            for i in incomingAck:
                i_string = i.to_string()
                i_tuple_ack = i_string.partition('ack: ')
                i_ack_string = i_tuple_ack[-1]
                i_ack_split = i_ack_string.split(",", 1)
                currentAck = int(i_ack_split[0])
            self.processAck = False

        if droppedAck:
            droppedAck = True
            missing = True
            num = self.segSent
            dropCounter = 1
            resendSegments = []
            createNewSegments = [self.dataToSend[i:i + n] for i in range(0, len(self.dataToSend), n)]
            for i in range(len(createNewSegments)):
                resendSegments.append((i, createNewSegments[i]))

            resendSegments.reverse()

            for i in resendSegments:
                if i[0] == (num/4):
                    segmentSend.setData((i[0]) * 4, i[1])
                    print("Sending segment: ", segmentSend.to_string())
                    self.sendChannel.send(segmentSend)
                    num -= 4
                    dropCounter += 1
                if dropCounter % (m+1) == 0:
                    break
            self.timeLimit = self.currentIteration

        # dropped packet
        if currentAck < 0:
            currentAck = (currentAck * -1) - 4
            missing = True
            dropped_retransmission = True
            findMissingSegment = []
            createMissingSegment = [self.dataToSend[i:i + n] for i in range(0, len(self.dataToSend), n)]
            for i in range(len(createMissingSegment)):
                findMissingSegment.append((i, createMissingSegment[i]))
            for i in range(len(findMissingSegment)):
                missingSegmentAck = (findMissingSegment[i][0] * 4)
                if missingSegmentAck == currentAck + 4:
                    segmentSend.setData(i * 4, findMissingSegment[i][1])
                    print("Sending segment: ", segmentSend.to_string())
                    # Use the unreliable sendChannel to send the segment
                    self.sendChannel.send(segmentSend)
                    segmentSend = Segment()
                    break
            self.timeLimit = self.currentIteration

        elif currentAck != self.segSent and not droppedAck and not dropped_retransmission:
            missing = True
            findMissingSegment = []
            createMissingSegment = [self.dataToSend[i:i+n] for i in range(0, len(self.dataToSend), n)]
            for i in range(len(createMissingSegment)):
                findMissingSegment.append((i, createMissingSegment[i]))
            for i in range(len(findMissingSegment)):
                missingSegmentAck = (findMissingSegment[i][0]*4)
                if missingSegmentAck == currentAck+4:
                    segmentSend.setData(i*4, findMissingSegment[i][1])
                    print("Sending segment: ", segmentSend.to_string())
                    # Use the unreliable sendChannel to send the segment
                    self.sendChannel.send(segmentSend)
                    segmentSend = Segment()
                    break
            self.timeLimit = self.currentIteration

        if not missing:
            self.processAck = True
            createSegment = [self.dataToSend[i:i+n] for i in range(0, len(self.dataToSend), n)]
            for i in self.sentDataList:
                if i in createSegment:
                    createSegment.remove(i)

            for i in range(len(createSegment)):
                segmentSend.setData(self.counter*4, createSegment[0])
                self.segSent = self.counter*4
                self.counter += 1
                self.sendingLimit += 1
                self.sentDataList.append(createSegment[0])
                createSegment.pop(0)
                # Display sending segment
                print("Sending segment: ", segmentSend.to_string())
                # Use the unreliable sendChannel to send the segment
                self.sendChannel.send(segmentSend)
                segmentSend = Segment()
                if self.sendingLimit % m == 0:
                    break


    # ################################################################################################################ #
    # processReceive()                                                                                                 #
    #                                                                                                                  #
    # Description:                                                                                                     #
    # Manages Segment receive tasks                                                                                    #
    #                                                                                                                  #
    #                                                                                                                  #
    # ################################################################################################################ #
    def processReceiveAndSendRespond(self):
        segmentAck = Segment()  # Segment acknowledging packet(s) received

        # This call returns a list of incoming segments (see Segment class)...
        listIncomingSegments = self.receiveChannel.receive()

        # ############################################################################################################ #
        # What segments have been received?
        # How will you get them back in order?
        # This is where a majority of your logic will be implemented
        # ############################################################################################################ #
        # How do you respond to what you have received?
        # How can you tell data segments apart from ack segments?
        # Somewhere in here you will be setting the contents of the ack segments to send.
        # The goal is to employ cumulative ack, just like TCP does...

        checkDroppedPackets = []
        goodChecksum = True
        goodChecksum_2 = True
        actually0 = False
        packetDropped = False
        retransmission = False
        if listIncomingSegments:
            if len(listIncomingSegments) == 2:
                retransmission = True
            for i in listIncomingSegments:
                goodChecksum = self.dataErrors(i)

                if goodChecksum is False:
                    goodChecksum_2 = False

                i_string = i.to_string()
                i_tuple_seq = i_string.partition('seq: ')
                i_seq_string = i_tuple_seq[-1]
                i_seq_split = i_seq_string.split(",", 1)

                if goodChecksum is False and i_seq_split[0] == "0":
                    actually0 = True

                if i_seq_split[0] != "-1":
                    i_tuple_data = i_string.partition('data: ')
                    self.dataReceivedList.append(i_tuple_data[-1])
                    self.receivedSegments[int(i_seq_split[0])] = i_tuple_data[-1]
                    checkDroppedPackets.append((int(i_seq_split[0]), i_tuple_data[-1]))

                    if goodChecksum_2:
                        self.acknum = int(i_seq_split[0])

                else:
                    break

            # https://stackoverflow.com/questions/44619572/join-the-values-only-in-a-python-dictionary
            # put together all data that has been received so far
            # packets will be sorted by key in dictionary, and put in order-- this solves the problem of the "outOfOrder" problem in the unreliable channel
            self.dataReceived = "".join(str(self.receivedSegments[i]) for i in sorted(self.receivedSegments))


            # ############################################################################################################ #
            # Display response segment

            x = self.dropPackets(checkDroppedPackets)

            if x[0]:
                packetDropped = True

            """if retransmission:
                retransmission = False
                segmentAck.setAck(self.acknum - 4)
                print("Sending ack: ", segmentAck.to_string())
                # Use the unreliable sendChannel to send the ack packet
                self.sendChannel.send(segmentAck)
                segmentAck = Segment()
                self.processAck = False"""
            if actually0:
                segmentAck.setAck(self.acknum-4)
                print("Sending ack: ", segmentAck.to_string())
                # Use the unreliable sendChannel to send the ack packet
                self.sendChannel.send(segmentAck)
                segmentAck = Segment()
                self.processAck = False
            elif packetDropped:
                segmentAck.setAck(-x[1])
                print("Sending ack: ", segmentAck.to_string())
                # Use the unreliable sendChannel to send the ack packet
                self.sendChannel.send(segmentAck)
                segmentAck = Segment()
                self.processAck = False
            else:
                segmentAck.setAck(self.acknum)
                print("Sending ack: ", segmentAck.to_string())
                # Use the unreliable sendChannel to send the ack packet
                self.sendChannel.send(segmentAck)
                segmentAck = Segment()
                self.processAck = False

        else:
            # send ack by client server
            segmentAck.setAck(0)
            print("Sending ack: ", segmentAck.to_string())
            # Use the unreliable sendChannel to send the ack packet
            self.sendChannel.send(segmentAck)
            segmentAck = Segment()
            self.ackClient += 1
            self.processAck = True

    def dataErrors(self, i):
        return i.checkChecksum()

    def dropPackets(self, checkPackets):
        droppedPackage = False
        packageNumber = ""
        needs_to_equal = 0
        for i in range(len(checkPackets) - 1):
            next_item = checkPackets[i + 1][0]
            needs_to_equal = checkPackets[i][0] + 4
            if next_item != needs_to_equal:
                droppedPackage = True
                packageNumber = needs_to_equal
                break
            if len(checkPackets) != 3 and checkPackets[0][0] == 4:
                # actually 0
                droppedPackage = True
                packageNumber = 4
            if len(checkPackets) != 3 and checkPackets[0][0] % 3 != 0:
                droppedPackage = True
                packageNumber = checkPackets[0][0] - 4

            if len(checkPackets) != 3 and i == 1:
                droppedPackage = True
                packageNumber = needs_to_equal+4


        return droppedPackage, packageNumber