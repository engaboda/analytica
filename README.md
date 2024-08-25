### Description
Analytica is a web application designed to help to upload, process <br>
and manipulating of various data types.

data types: <br>
1. tabular data.
2. RGB Images.
3. Textual data

## tabular data <br>
we will use pandas library to deal with Tabular Data. <br>
following apis will be building. <br>

```
1. Upload File.
2. List All Files.
3. Delete File.
4. Details Api for file.
5. Get Head of Tabular file.
6. Show information about tabular file.
7. Delete Row.
8. Show specific Column.
9. Get Mean for Specific Column.
10. Get Median for Specific Column.
11. Get Quantile for Specific Column.
12. Select with query.
13. Select With Complex Query.
```

### while pandas
pandas can deal with all type of tabular data like csv, sql and much more.<br>
easy to use and has big community to help if we stuck in very hard problems.


## Textual data <br>
we will use elastic search for doing search and categorization and we will use
Rake library to handle keyword extraction.

```
1. keyword extraction.
2. search.
3. categorization using MLT algorithim from elastic search.
4. show all documents in elastic.
```

### why elastic search
elastic is very easy to user has very big community also has very nice dashboard (kibana).<br>
elastic will help us to do very complex query over string documents and doing some NL actions.<br>


## RGB Images <br>
we will use PIL to manipulate images.
```
1. Upload Image.
2. Resize Image.
3. Crop Image.
```

### why PIL
because after search i found PIL gives me all APIs to be able to doing image processing.
also it has very big community and nice documentation to follow.


## to run the project
`docker compose -f docker-compose.dev.yml up --build`

1. docker-compose.dev.yml `this file for production deployment`
2. docker-compose.local.yml `this file exclude BE for easy development`


## you can also find postman collection `Analysita.postman_collection.json`
you can import it in post man and try with your own. when run prod compose file <br>

url will be: http://localhost/api/... <br>
and when using local one url will be: http://localhost:5000/api/...


## to run tests
`python -m unittest discover`


## Time Allocation
doing search and development take most of the time, 2 days and half, <br>
while preparing for deployment it takes half day.


# Methodology
my methodology while building any app trying to make everything readable <br>
while adding test because test act like documentation.

writing piece of code then test it, sometime, i follow TDD for better outcomes.
building the app from start to have very easy deployment process.