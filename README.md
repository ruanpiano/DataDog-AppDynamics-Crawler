# DataDog-AppDynamics-Crawler
Lots of people asks me if there is an integration between DataDog and AppDynamics. This integration solves this issue. **This isn't a official DataDog supported integration, try it on your own.**

The main purpose of this project is to push AppDynamics data into DataDog metrics through both APIs.

You need to set the following environment variables in the **env.sh** file as the example above:

    export DD_API_KEY=064881afa8602afc8cbce508ea1119df
    export DD_APP_KEY=c842553543ca6af83686545a1d1f5501cdbd57da
    export APPD_CONTROLLER=customer1.saas.appdynamics.com
    export APPD_PROTOCOL=https://
    export APPD_FORMAT=?output=JSON
    export APPD_USER=ruanpiano@customer1
    export APPD_PASS=ruanpiano
    export DEBUG=true

## Up and Running
### Using Docker as base
Build your image using the command

    docker build . -t datadog-appdynamics-crawler

Run your container with the following command

    docker run -dit datadog-appdynamics-crawler

