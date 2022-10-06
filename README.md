## PII Anonymizer
This is a dockerized Flask app for anonymizing Personal Identifiable 
Information (PII) in text, such as person name, phone number, credit card 
etc.
The docker image can be deployed both on premise or to the cloud 
(This repository contains example scripts
for deploying to AWS).

The app utilize the [Presidio](https://microsoft.github.io/presidio/)
library for detecting and anonymizing PII. The supported entities can be 
found [here](https://microsoft.github.io/presidio/supported_entities/).
Currently this app only support PII anonymization for texts in
English and Norwegian.

## Getting started
### Deploy the app locally as Rest API and invoke it

Run `start_up.sh` from the root directory, with optionally two argument for image name and the port number. For example:

```
./start_up.sh pii-anonymizer 8989
```

This script does two things 
  1) Build docker image with the provided name, if not provided, the name is by default `pii-anonymizer`
  2) Serves the docker app, listing to the provided port at the host machine, by default the port number is 8989 

Subsequently, you can invoke by running
    
```
scripts/predict.sh data/input.json
```

The API expected text data in JSON format as following:
```
{"input":
  [
    {"text" : "Hello Paulo Santos. The latest statement for your credit card account 1111-0000-1111-0000 was mailed to 123 Any Street, Seattle, WA 98109.", "lang": "en"},
    {"text" : "My phone number is 212-555-5555", "lang": "en"},
    {"text": "Hello this is Jamie Clark calling", "lang": "en"},
  ],
  "mode": "tagged_text"
}
```

the `"lang"` field specifies the language of the text, currently 
supports `"en", "no" or "unknown"`. Specifying the language would 
save time for the anonymizer, since it does not need to load the 
language detection module and run the detector. 
Choices for the `"mode"` filed includes `"tagged_text"` for getting
result with PII masked with tags such as <PERSON>, <EMAIL>. 
For example:
```
{
  "output": {
    "output": [
      {
        "tagged_text": "Hello <PERSON>. The latest statement for your credit card account <CREDIT_CARD> was mailed to 123 Any Street, <LOCATION>, WA 98109."
      },
      {
        "tagged_text": "My phone number is <PHONE_NUMBER>"
      },
      {
        "tagged_text": "Hello this is <PERSON> calling"
      }
    ]
  }
}
```

`"detailed_info"` for getting detailed result per PII which
contains the start index, end index, entity type and entity itself. For example:
```
{
  "output": {
    "output": [
      {
        "detailed_info": [
          {
            "entity_type": "PERSON",
            "start": 6,
            "end": 18,
            "score": 0.85,
            "entity": "Paulo Santos"
          },
          {
            "entity_type": "LOCATION",
            "start": 120,
            "end": 127,
            "score": 0.85,
            "entity": "Seattle"
          }
        ]
      },
      {
        "detailed_info": [
          {
            "entity_type": "PHONE_NUMBER",
            "start": 19,
            "end": 31,
            "score": 0.75,
            "entity": "212-555-5555"
          }
        ]
      },
      {
        "detailed_info": [
          {
            "entity_type": "PERSON",
            "start": 14,
            "end": 25,
            "score": 0.85,
            "entity": "Jamie Clark"
          }
        ]
      }
    ]
  }
}
```

### Deploy to AWS

1. #### Push the image to ECR 
    Push the image to ECR by running following command from `/container` directory
    ```
    ./build_and_push.sh
    ```
   
2. #### Create and configure cluster in AWS ECS
3. #### Create a task definition
4. #### Start a service


