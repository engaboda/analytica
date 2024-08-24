### Description
Analysita is a web application designed to help to upload, process <br>
and manipulating of various data types.

data types: <br>
1. tabular data.
2. TGB Images.
3. Textual data

## tabular data <br>
we will use pandas library to deal with this type. <br>
following apis will be building. <br>

```
1. Upload File.
2. List All Files.
3. Delete File.
4. Details Api for file.
5. Get HEad of Tabular file.
6. Show information about tabular file.
7. Delete Row.
8. Show specific Column.
9. Get Mean for Specific Column.
10. Get Median for Specific Column.
11. Get Quantile for Specific Column.
12. Select with query.
13. Select With Complex Query.
```


## Textual data <br>
we will use elastic search for doing search and categorization and we will use
Rake library to handle keyword extraction.

```
1. keyword extraction.
2. search.
3. categorization using MLT algorithim from elastic search
```

## RGB Images <br>
we will use PIL to manipulate images.
```
1. Upload Image.
2. Resize Image.
3. Crop Image.
```


## to run the project
`docker compose up -f docker-compose.dev.yml --build`
1. docker-compose.dev.yml `this file for production deployment`
2. docker-compose.local.yml `this file exclude BE for easy development`

## you can also find postman collection `Analysita.postman_collection.json`

## to run tests
`python -m unittest discover`
