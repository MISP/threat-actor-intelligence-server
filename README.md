# threat-actor-intelligence-server

![](https://raw.githubusercontent.com/MISP/threat-actor-intelligence-server/main/doc/logo/tai.png)

A simple ReST server to lookup threat actors (by name, synonym or UUID) and returning the corresponding MISP galaxy information about the known threat actors.

# Requirements

- Python 3.6
- Tornado

# Installation

~~~
git clone https://github.com/MISP/threat-actor-intelligence-server
cd threat-actor-intelligence-server
git submodule init
git submodule update
pip install -r REQUIREMENTS
~~~
## Starting the server

~~~
cd bin
python tai-server.py
~~~

By the default, the server is listening on TCP port 8889.

# Alternative Installation

This method involves:
 - installing a few dependencies
 - creating a dedicated, unprivileged, user to run the TAI server(s)
 - creating a python virtual environment
 - installation of TAI
 - systemd configuraion of (arbitrarily) four instances
 - configuring nginx as a reverse proxy to four instances

Installing a few dependencies
~~~
sudo apt install virtualenv git python3-pip nginx
~~~

Create a dedicated, unprivileged, user to run the TAI server(s)
~~~
sudo adduser tai
~~~

Create and activate a python virtual environment called _tai-env_
~~~
sudo su tai 
virtualenv tai-env
source ./tai-env/bin/activate
~~~

Installation of TAI in the home directory of the user `tai`
~~~
cd
git clone https://github.com/MISP/threat-actor-intelligence-server
cd threat-actor-intelligence-server
git submodule init
git submodule update
pip install -r REQUIREMENTS
exit
~~~

systemd configuraion for a group of four instances of TAI
~~~
sudo cp /home/tai/threat-actor-intelligence-server/debian/tai@.service /lib/systemd/system/
sudo cp /home/tai/threat-actor-intelligence-server/debian/tai.target /etc/systemd/system/
sudo systemctl daemon-reload
~~~

configuring nginx as a reverse proxy to four instances
~~~
sudo rm /etc/nginx/site-enabled/default
sudo cp /home/tai/threat-actor-intelligence-server/debian/nginx-tai.conf /etc/nginx/sites-available/
sudo ln -s /etc/nginx/sites-available/nginx-tai.conf /etc/nginx/sites-enabled/
~~~

Lastly, configure systemd to start the TAI servers and nginx automatically
~~~
sudo systemctl enable tai.target
sudo systemctl enable nginx
~~~

## Docker Installation

You can run the Threat Actor Intelligence Server using Docker for a simplified deployment.

### Prerequisites
- Install [Docker](https://docs.docker.com/get-docker/).
~~~bash
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
~~~

### Setup

- **Clone the repository**:
   ~~~bash
   git clone https://github.com/MISP/threat-actor-intelligence-server
   cd threat-actor-intelligence-server
   ~~~

### Running the Server
- **Using Docker Compose** (recommended):
  ~~~bash
  docker compose up --build -d
  ~~~
  This builds and starts the container in detached mode. The server listens on `http://localhost:8889`.

- **Using Docker**:
  ~~~bash
  docker build -t threat-actor-intelligence-server .
  docker run -d -p 8889:8889 threat-actor-intelligence-server
  ~~~

### Verify
- Check the container logs to confirm the server started and `threat-actor.json` was found:
  ~~~bash
  docker compose logs
  ~~~
  or
  ~~~bash
  docker logs <container_id>
  ~~~
- Test the API at `http://localhost:8889/query` (e.g., `curl -d '{"name":"APT34"}' -H "Content-Type: application/json" -X POST http://localhost:8889/query`).


# API and public API

The API is simple and can be queried on the `/query` entry point by POSTing a simple query in JSON format. The query format is 
composed of an `name` as key or an `uuid` as key. The output format is a JSON in the [MISP standard galaxy format](https://www.misp-standard.org/rfc/misp-standard-galaxy-format.txt). 

Query such as `{"name":"APT34"}` or `{"name":"Sofacy"}` does the search on the name or potential synonyms.

There is also a simple GET entry point `/get/<UUID>` entry point followed by the UUID of the threat-actor.

- [https://www.misp-project.org/tai/get/103ebfd8-4280-4027-b61a-69bd9967ad6c](https://www.misp-project.org/tai/get/103ebfd8-4280-4027-b61a-69bd9967ad6c) which returns the entries for a specific threat-actor.

A public API is available at the following url `https://www.misp-project.org/tai/` and can be queried to gather the latest information about threat-actors.

## Example using curl 

~~~json
curl --silent -d '{"name":"APT34"}' -H "Content-Type: application/json" -X POST https://www.misp-project.org/tai/query | jq . 
[
  {
    "description": "Since at least 2014, an Iranian threat group tracked by FireEye as APT34 has conducted reconnaissance aligned with the strategic interests of Iran. The group conducts operations primarily in the Middle East, targeting financial, government, energy, chemical, telecommunications and other industries. Repeated targeting of Middle Eastern financial, energy and government organizations leads FireEye to assess that those sectors are a primary concern of APT34. The use of infrastructure tied to Iranian operations, timing and alignment with the national interests of Iran also lead FireEye to assess that APT34 acts on behalf of the Iranian government.",
    "meta": {
      "attribution-confidence": "50",
      "cfr-suspected-state-sponsor": "Iran (Islamic Republic of)",
      "cfr-suspected-victims": [
        "Middle East"
      ],
      "cfr-target-category": [
        "Government",
        "Private sector"
      ],
      "cfr-type-of-incident": "Espionage",
      "country": "IR",
      "refs": [
        "https://www.fireeye.com/content/dam/collateral/en/mtrends-2018.pdf",
        "https://www.wired.com/story/apt-34-iranian-hackers-critical-infrastructure-companies/  ",
        "https://www.fireeye.com/blog/threat-research/2017/12/targeted-attack-in-middle-east-by-apt34.html",
        "https://www.cfr.org/interactive/cyber-operations/apt-34"
      ],
      "synonyms": [
        "APT 34"
      ]
    },
    "related": [
      {
        "dest-uuid": "68ba94ab-78b8-43e7-83e2-aed3466882c6",
        "tags": [
          "estimative-language:likelihood-probability=\"likely\""
        ],
        "type": "similar"
      }
    ],
    "uuid": "73a521f6-3bc7-11e8-9e30-df7c90e50dda",
    "value": "APT34"
  }
]
~~~
## Example to query threat-actors by country

~~~json
curl --silent -d '{"country":"FR"}' -H "Content-Type: application/json" -X POST https://www.misp-project.org/tai/query | jq .
[
  {
    "description": "In 2014, researchers at Kaspersky Lab discovered and reported on three zero-days that were being used in cyberattacks in the wild. Two of these zero-day vulnerabilities are associated with an advanced threat actor we call Animal Farm. Over the past few years, Animal Farm has targeted a wide range of global organizations. The group has been active since at least 2009 and there are signs that earlier malware versions  were developed as far back as 2007.",
    "meta": {
      "attribution-confidence": "50",
      "cfr-suspected-state-sponsor": "France",
      "cfr-suspected-victims": [
        "Syria",
        "United States",
        "Netherlands",
        "Russia",
        "Spain",
        "Iran",
        "China",
        "Germany",
        "Algeria",
        "Norway",
        "Malaysia",
        "Turkey",
        "United Kingdom",
        "Ivory Coast",
        "Greece"
      ],
      "cfr-target-category": [
        "Government",
        "Private sector"
      ],
      "cfr-type-of-incident": "Espionage",
      "country": "FR",
      "refs": [
        "https://securelist.com/blog/research/69114/animals-in-the-apt-farm/",
        "https://motherboard.vice.com/read/meet-babar-a-new-malware-almost-certainly-created-by-france",
        "http://www.cyphort.com/evilbunny-malware-instrumented-lua/",
        "http://www.cyphort.com/babar-suspected-nation-state-spyware-spotlight/",
        "https://www.gdatasoftware.com/blog/2015/02/24270-babar-espionage-software-finally-found-and-put-under-the-microscope",
        "https://www.cfr.org/interactive/cyber-operations/snowglobe",
        "https://resources.infosecinstitute.com/animal-farm-apt-and-the-shadow-of-france-intelligence/"
      ],
      "synonyms": [
        "Animal Farm",
        "Snowglobe"
      ]
    },
    "uuid": "3b8e7462-c83f-4e7d-9511-2fe430d80aab",
    "value": "SNOWGLOBE"
  }
]
~~~

## Example to query a threat-actor by UUID

~~~json
curl --silent -d '{"uuid":"0286e80e-b0ed-464f-ad62-beec8536d0cb"}' -H "Content-Type: application/json" -X POST https://www.misp-project.org/tai/query  | jq .
{
  "description": "We have investigated their intrusions since 2013 and have been battling them nonstop over the last year at several large telecommunications and technology companies. The determination of this China-based adversary is truly impressive: they are like a dog with a bone.\nHURRICANE PANDA’s preferred initial vector of compromise and persistence is a China Chopper webshell – a tiny and easily obfuscated 70 byte text file that consists of an ‘eval()’ command, which is then used to provide full command execution and file upload/download capabilities to the attackers. This script is typically uploaded to a web server via a SQL injection or WebDAV vulnerability, which is often trivial to uncover in a company with a large external web presence.\nOnce inside, the adversary immediately moves on to execution of a credential theft tool such as Mimikatz (repacked to avoid AV detection). If they are lucky to have caught an administrator who might be logged into that web server at the time, they will have gained domain administrator credentials and can now roam your network at will via ‘net use’ and ‘wmic’ commands executed through the webshell terminal.",
  "meta": {
    "attribution-confidence": "50",
    "country": "CN",
    "refs": [
      "http://www.crowdstrike.com/blog/cyber-deterrence-in-action-a-story-of-one-long-hurricane-panda-campaign/",
      "https://blog.confiant.com/uncovering-2017s-largest-malvertising-operation-b84cd38d6b85",
      "https://blog.confiant.com/zirconium-was-one-step-ahead-of-chromes-redirect-blocker-with-0-day-2d61802efd0d"
    ],
    "synonyms": [
      "Black Vine",
      "TEMP.Avengers",
      "Zirconium",
      "APT 31",
      "APT31"
    ]
  },
  "related": [
    {
      "dest-uuid": "a653431d-6a5e-4600-8ad3-609b5af57064",
      "tags": [
        "estimative-language:likelihood-probability=\"likely\""
      ],
      "type": "similar"
    },
    {
      "dest-uuid": "066d25c1-71bd-4bd4-8ca7-edbba00063f4",
      "tags": [
        "estimative-language:likelihood-probability=\"likely\""
      ],
      "type": "similar"
    },
    {
      "dest-uuid": "103ebfd8-4280-4027-b61a-69bd9967ad6c",
      "tags": [
        "estimative-language:likelihood-probability=\"likely\""
      ],
      "type": "similar"
    }
  ],
  "uuid": "0286e80e-b0ed-464f-ad62-beec8536d0cb",
  "value": "Hurricane Panda"
}
~~~

# License and author(s)

This software is free software and licensed under the AGPL version 3.

Copyright (c) 2020 Alexandre Dulaunoy - https://github.com/adulau/

# Contributing

We welcome contributions. Every contributors will be added in the [AUTHORS file](./AUTHORS) and collectively own this open source software. The contributors acknowledge the [Developer Certificate of Origin](https://developercertificate.org/).

If you want to contribute threat-actor information, we welcome you to make a pull-request on the [misp-galaxy repository](https://github.com/MISP/misp-galaxy/blob/master/clusters/threat-actor.json).

