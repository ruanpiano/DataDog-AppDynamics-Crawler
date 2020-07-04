# DataDog-AppDynamics-Crawler
Lots of people asks me if there is an integration between DataDog and AppDynamics. This integration solves this issue. **This isn't a official DataDog supported integration, try it on your own.**

The main purpose of this project is to push AppDynamics data into DataDog metrics through both APIs.

You need to set the following environment variables as the example above:

    DD_API_KEY = "064881afa8602afc8cbce508ea1119df"
    DD_APP_KEY = "c842553543ca6af83686545a1d1f5501cdbd57da" 
    APPD_CONTROLLER = "customer1.saas.appdynamics.com"
    APPD_PROTOCOL = "https://"
    APPD_FORMAT = "?output=JSON"
    APPD_USER = "ruanpiano@customer1"
    APPD_PASS = "ruanpiano"
