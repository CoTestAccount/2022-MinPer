#!/bin/bash

input="channel_id.txt"
output="channel_details.txt"


rm ${output}
touch ${output}

while IFS= read -r line
do

      script="query { 
  applet(id: \\\"${line}\\\"){
    id
    filter_code
    description
    name
    published
    archived
    channel_id
    channel_module_name
    installs_count
    
    triggers {
      id name
      description
      ingredients {
        name
        slug
        note
        label
        example
        normalized_name
      }
      
      trigger_fields {
        name
        slug
        normalized_field_type
        field_type
      }
    }
    
    actions {
      id name
    }
    
    
  }
}"
      script="$(echo $script)"
      

      command=$(curl -k -L -s  --compressed 'https://ifttt.com/api/v3/graph' \
      -X POST \
      -d "{ \"query\": \"$script\"}"  \
      -H 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:99.0) Gecko/20100101 Firefox/99.0' \
      -H 'Accept: */*' -H 'Accept-Language: en-US,en;q=0.5' -H 'Accept-Encoding: gzip, deflate, br' \
      -H 'Referer: https://ifttt.com/data/graphiql' -H 'Content-Type: application/json' \
      -H 'Authorization: Token token="5fcfbfff07add34afe3fa7b20b5b60ae9dd00b7a"' \
      -H 'X-CSRF-Token: ucHKaKb4SQFSZHTbg7DL6k6ONPQrINFJjgfohB11h60KPdT4anecPWSiJXWv7pGxWYUGTDKDAF35G4dNyL0o1A==' \
      -H 'Origin: https://ifttt.com' -H 'Connection: keep-alive' \
      -H 'Cookie: _anon_id=ImZjYTQ4MjRlNDdlYTZlYjc4Y2M0MmRjMGE0ZGZlMjkzIg%3D%3D--1686544f558da4ad5627ed630bf305c559a0a8d8; _ga=GA1.2.69013591.1647322994; rl_anonymous_id=RudderEncrypt%3AU2FsdGVkX19RaaOaQoHJvMjeTNT2JK4dJftYzxaZkbAYWxB08HZj9dKGYAprsLU5dIjCBPJmMqH5m4kPdEZCOQ%3D%3D; rl_user_id=RudderEncrypt%3AU2FsdGVkX187mR4GZaV%2BjUgfzvxrRhH6m6ueKFxTQ1w%3D; rl_group_id=RudderEncrypt%3AU2FsdGVkX1%2BttP6iwEukj5Sb2O3tj86GsnywHxHbxds%3D; rl_trait=RudderEncrypt%3AU2FsdGVkX18vQYG0MEH5bJEeUSFnR%2BnUxGKsHIc8uTudn0F3Gqu2vbM6JhbecXubz1vIkGR4sA5xPLu0AulqoMGgvuNq05wtZZzv2JrjD6A%3D; rl_group_trait=RudderEncrypt%3AU2FsdGVkX19HRLRGOw2%2B%2FpTueACCjgMDkxA6xfj5Y%2FE%3D; _fbp=fb.1.1648440613519.65855801; G_ENABLED_IDPS=google; remember_token=5fcfbfff07add34afe3fa7b20b5b60ae9dd00b7a; auth_cdn_cache_key=bc7da1f39e4db61b; iter_id=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhaWQiOiI2MjQzZDIzYmYxMDI4MDAwMDFlMWUyZDEiLCJjb21wYW55X2lkIjoiNWQ2OWExN2IyNDI3ZTUwMDAxY2RiYWI4IiwiaWF0IjoxNjQ4NjExODk5fQ.Mn1Sp_4EbHf-Pf9qKe3wbW3N3kOxQuqmaQbeA68mhqQ; shared_user_id=27468860; __utma=106609372.69013591.1647322994.1648985790.1648985790.1; __utmz=106609372.1648985790.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); most_recent_service_slug=hello_world_11b71865aa; __stripe_mid=4ed5d319-58a0-4218-8fc1-dcacae78754450fce5; timezone=Australia/Brisbane; _gid=GA1.2.1174163417.1649992456; _ifttt_front_end_session=Z29BM1V0dmNMQjlmbjIyMVJSaUVkSWl2V0huTGdmMCtTdGgrcGorZ3NOMkF5T3VuUDBFT0s5T2JBZW5aVi9taHYvbDVMT1JEUWphR2xkZFBpTy8vNkhuZjl6OGlJZlI0K015MjYvMitRVUhTQTB6V0FEL04zbTg5THllamNWZFlYa0VleDhtZ1ViNmN4SkRmd29JOEp3PT0tLVFnZHNZbnZSU3VGeWJGKzRJZlFlRFE9PQ%3D%3D--65996cc09f36e6382536b60c904291d892f88c6f; browser_session_id=Koc_fT-q8CF_FuZ-316Xvg; _applet_service_session=UHFpUGVZaDBSRWxTTzRqWU1VdGtKZmNSWll1V0g4Zm9CTStzMnZEUzVVTkdtNnJqa3NKK2I0V3lCSTUxcUcvcDVKQUZQdUZkbnFuVDFhWHYrOEwyNFJNRFVKSHEyY1hXUUJXZ2xweUdJNWpjd2ZNN0t6VEh3QWVkRytZYXFnaWRQd2FmNGNnWEovUzA4cWtJbFYvREFCWE1vdW9xd3pXQnBydXN6Z21MSDlDNFJNdXJNeUtLTlVjVFBrWFBOS3VaUHpxQ3ZvTUhoU2xRYWVXd2VHOHRhUjJjeElJbi85VXhhN1VMYWRJYzNpdHpSZ0xUdHVkQmk4VjZVUVlaQjNRMWw0cEdGdHpWTlExaXg0WkFUWndIclZ6cDEzWlY2U0RUU3BER3dUUi8rVjAwUkZBYTJzaHRueUJOL0d6VWQ4NEtkZTdBRVNMdDE2MmFUeFdZOEZiTFVLaXNneDVaTXRSc2ExNE9GS0tYeEhUeStxRUoyWExPMWRqMlpqb0dwOXl3LS1nVmZSL3JzVzdWWTZRd1JpeTR1Tmt3PT0%3D--e89a4528ea6bc9191822d94cc0f1d5d57e3cd02f' \
      -H 'Sec-Fetch-Dest: empty' -H 'Sec-Fetch-Mode: cors' -H 'Sec-Fetch-Site: same-origin' \
      -H 'TE: trailers')
      echo ${command} >> ${output}


done <"${input}"
