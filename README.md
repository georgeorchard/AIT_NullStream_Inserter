# AIT_NullStream_Inserter
Used for inserting AITs into a null stream for muxing.

Run with command line args of the JSON file name where the AIT info is stored and the output IP.

python AIT_Inserter.py AIT_Definitions.json 

JSON Settings:
Update SetUp like this:

"setUp": [
      {
      
        "outputMode": "IP",
        
        "outputIP": "192.168.0.1",
        
        "outputPort": 1234,
        
        "bitRate": 1000000,
        
        "fileLengthSeconds": 5,
        
        "outputFileName": "output.ts"
        
      }
      
    ],
    
Where outputMode IP outputs to the IP stream and outputMode file outputs to a defined file.



Input AIT settings like this, as many as needed:

"AITs": [
      {
      
        "url": "https://bci-staging-media.s3.eu-west-1.amazonaws.com/HBBTV_test_area/hbbtv-tests/testApp/dev/",
        
        "initialPath": "index.html?debug=1&api=staging&serviceid=99997",
        
        "pid": 901
        
      },
      
      {
      
        "url": "https://bci-staging-media.s3.eu-west-1.amazonaws.com/HBBTV_test_area/hbbtv-tests/testApp/George/",
        
        "initialPath": "index.html?debug=1&api=staging&serviceid=99998",
        
        "pid": 902
        
      },
      
      {
      
        "url": "https://bci-staging-media.s3.eu-west-1.amazonaws.com/HBBTV_test_area/hbbtv-tests/testApp/Rich/",
        
        "initialPath": "index.html?debug=1&api=staging&serviceid=99999",
        
        "pid": 903
        
      }
      
    ]
    
