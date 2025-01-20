import json
from sys import argv
import xml.etree.ElementTree as ET
import subprocess
import time
import os



def createXMLsFromJSONFile(jsonFile):
    """
    Function to create the XMLs for each individual AIT component defined in the JSON File
    Params: jsonFile - JSON File containing the AIT components
    """
    #Set a count variable to count the number of AITs created
    ait_count = 0

    #Create a list to store the AIT PIDs
    aitPIDs = []

    #Open the JSON File
    with open(jsonFile) as f:
        data = json.load(f)

        #Get information from set-up
        setUp_Information = data['setUp'][0]
        outputMode = setUp_Information['outputMode']
        outputIP = setUp_Information['outputIP']
        outputPort = setUp_Information['outputPort']
        bitRate = setUp_Information['bitRate']
        fileLengthSeconds = setUp_Information['fileLengthSeconds']
        outputFileName = setUp_Information['outputFileName']



        for i in data['AITs']: #Access the AIT components

            #Increment the AIT count
            ait_count += 1

            #Load the variables from the JSON File and some hard coded.
            applicationID = "0x00C9"
            organizationID = "0x0000001A"
            url = i['url']
            applicationProfile = "0x0000"
            applicationVersion = "1.1.1"
            applicationName = "AppName"
            initialPath = i['initialPath']
            pid = i['pid']

            #Append the PID to the aitPIDs List
            aitPIDs.append(pid)

            #Create the XML for this individual AIT component - will be saved as ait[i].xml
            createAITXML(applicationID, organizationID, url, applicationProfile, applicationVersion, applicationName, initialPath, ait_count)

    #Now that all AITs have been created, insert them into the stream 
    #If the output mode is IP, call the function to insert AITs into the stream using IP
    if outputMode == "IP":
        insertAITsIntoStream_IP(ait_count, aitPIDs, bitRate, outputIP, outputPort)
    #Otherwise call the function to insert AITs into the stream using a FILE
    else:
        insertAITsIntoStream_File(ait_count, aitPIDs, bitRate, fileLengthSeconds, outputFileName)
                 

def insertAITsIntoStream_IP(ait_count, aitPIDs, bitRate, outputIP, outputPort):
    """
    Function to inject raw AIT XMLs into the stream using TSDuck to create a FILE
    Params: 
        ait_count - The number of AITs to inject (e.g., 3 for aitXML1.xml, aitXML2.xml, etc.)
        aitPIDs - The list of PIDs corresponding to each AIT
        bitRate - The bitrate of the stream in bps
        fileLengthSeconds - The length of the file in seconds
        outputFileName - The name of the output file
    """

    # Check if the number of PIDs matches the number of AITs
    if len(aitPIDs) != ait_count:
        raise ValueError("The number of AIT PIDs must match the AIT count.")

    # Calculate packets per second based on the bitrate
    packetRate = round(bitRate / (188 * 8))  # 188 bytes per packet, 8 bits per byte

    # Base tsp command to create a null stream
    tsp_command = [
        "tsp",
        "-I", "null",  # Start with a null stream
        "-P", "regulate",
        "--bitrate", str(bitRate)  # Set the bitrate
    ]

    # Loop over each AIT XML and add to the tsp command
    for i in range(ait_count):
        ait_xml_file = f"aitXML{i+1}.xml"  # Generate the XML file name (e.g., aitXML1.xml)

        pid = aitPIDs[i]  # Get the corresponding PID for this AIT
        tsp_command += [
            "-P", "inject", ait_xml_file+"=1000",  # Inject the AIT XML file with 1000ms interval
            "--pid", str(pid),  # Set the PID for the AIT
            "--inter-packet", str(packetRate)  # Set the interval to 665 packets which is one packet a second at 1000000
        ]

    # Output the final stream to the specified IP address
    tsp_command += [
        "-O", "ip", "--packet-burst 7 --enforce-burst", str(outputIP)+":"+str(outputPort)  # Output to an IP
    ]


    print(f"Running TSDuck command: {' '.join(tsp_command)}")

    # Run the TSDuck command
    try:
        process = subprocess.Popen(tsp_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        if process.returncode == 0:
            print("AIT injection and stream output completed successfully.")
        else:
            print(f"Error in TSDuck processing: {stderr.decode('utf-8')}")
    except Exception as e:
        print(f"An error occurred: {e}")

def insertAITsIntoStream_File(ait_count, aitPIDs, bitRate, fileLengthSeconds, outputFileName):
    """
    Function to inject raw AIT XMLs into the stream using TSDuck to create a FILE
    Params: 
        ait_count - The number of AITs to inject (e.g., 3 for aitXML1.xml, aitXML2.xml, etc.)
        aitPIDs - The list of PIDs corresponding to each AIT
        bitRate - The bitrate of the stream in bps
        fileLengthSeconds - The length of the file in seconds
        outputFileName - The name of the output file
    """

    # Check if the number of PIDs matches the number of AITs
    if len(aitPIDs) != ait_count:
        raise ValueError("The number of AIT PIDs must match the AIT count.")

    # Calculate packets per second based on the bitrate
    packetRate = round(bitRate / (188 * 8))  # 188 bytes per packet, 8 bits per byte
    
    # Calculate the number of packets to generate based on the packet rate and file length
    numPackets = round(packetRate * fileLengthSeconds)

    # Base tsp command to create a null stream
    tsp_command = [
        "tsp",
        "-I", "null", str(numPackets),  # Start with a null stream
        "-P", "regulate",
        "--bitrate", str(bitRate)  # Set the bitrate
    ]

    # Loop over each AIT XML and add to the tsp command
    for i in range(ait_count):
        ait_xml_file = f"aitXML{i+1}.xml"  # Generate the XML file name (e.g., aitXML1.xml)

        pid = aitPIDs[i]  # Get the corresponding PID for this AIT
        tsp_command += [
            "-P", "inject", ait_xml_file+"=1000",  # Inject the AIT XML file with 1000ms interval
            "--pid", str(pid),  # Set the PID for the AIT
            "--inter-packet", str(packetRate)  # Set the interval to 665 packets which is one packet a second at 1000000
        ]

    # Output the final stream to the specified IP address
    tsp_command += [
        "-O", "file", "output.ts"  # Output to a file 
    ]


    print(f"Running TSDuck command: {' '.join(tsp_command)}")

    # Run the TSDuck command
    try:
        process = subprocess.Popen(tsp_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        if process.returncode == 0:
            print("AIT injection and stream output completed successfully.")
        else:
            print(f"Error in TSDuck processing: {stderr.decode('utf-8')}")
    except Exception as e:
        print(f"An error occurred: {e}")



def createAITXML(applicationID, organizationID, url, applicationProfile, applicationVersion, applicationName, initialPath, ait_count):
    """
    Function to create the AIT XML file given the correct parameters
    Params: applicationID - Application ID
            organizationID - Organization ID
            url - URL
            applicationProfile - Application Profile
            applicationVersion - Application Version
            applicationName - Application Name
            initialPath - Initial Path
            iterationNumber - The iteration number of the AIT component
    """
    # Create the root element
    root = ET.Element("tsduck")

    # Create the AIT element with attributes
    ait = ET.SubElement(root, "AIT")
    ait.set("application_type", "0x0010")
    ait.set("current", "true")
    ait.set("test_application_flag", "false")
    ait.set("version", "1")
    
    
    

    # Create the application element
    application = ET.SubElement(ait, "application")
    application.set("control_code", "0x01")

    # Create the application_identifier element
    app_identifier = ET.SubElement(application, "application_identifier")
    app_identifier.set("application_id", f"{applicationID}")
    app_identifier.set("organization_id", f"{organizationID}")
    

    # Create the transport_protocol_descriptor element
    tp_descriptor = ET.SubElement(application, "transport_protocol_descriptor")
    tp_descriptor.set("transport_protocol_label", "0x01")

    # Create the http element
    http = ET.SubElement(tp_descriptor, "http")

    # Create the url element with the 'base' attribute
    url_element = ET.Element("url", base=url)

    # Append the url element to the http element
    http.append(url_element)

    # Create the application_descriptor element
    app_descriptor = ET.SubElement(application, "application_descriptor")
    app_descriptor.set("application_priority", "1")
    app_descriptor.set("service_bound", "true")
    app_descriptor.set("visibility", "3")
    
    

    # Create the profile element
    profile = ET.SubElement(app_descriptor, "profile")
    profile.set("application_profile", f"{applicationProfile}")
    profile.set("version", f"{applicationVersion}")
    
    

    # Create the transport_protocol element
    transport_protocol = ET.SubElement(app_descriptor, "transport_protocol")
    transport_protocol.set("label", "0x01")

    # Create the application_name_descriptor element
    app_name_descriptor = ET.SubElement(application, "application_name_descriptor")

    # Create the language element
    language = ET.SubElement(app_name_descriptor, "language")
    language.set("application_name", f"{applicationName}")
    language.set("code", "eng")
    

    # Create the simple_application_location_descriptor element
    location_descriptor = ET.SubElement(application, "simple_application_location_descriptor")
    location_descriptor.set("initial_path", f"{initialPath}")

    # Create an ElementTree object with the root element
    tree = ET.ElementTree(root)

    # Save the XML to a file
    tree.write(f"aitXML{ait_count}.xml")


if __name__ == "__main__":
    #The JSON File path is the first argument from the command line
    ait_json_file = argv[1]

    #Call the function to create the XMLs from the JSON File
    createXMLsFromJSONFile(ait_json_file)
    
