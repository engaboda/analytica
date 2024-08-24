from src.apis import (
    TabularApi, TabularHead, TabularSelect, TabularSelectWithQuery, TabularInfo, TabularSelectWithComplexQuery,
    TabularMeanApi, TabularMedianApi, TabularModeApi, TabularQuantileApi, TabularDeleteApi, TabularUpdateDataSetApi,
    TextKeywordExtraction, ClassificationApi, TextFullSearch, UploadImageApi, ImageResizerApi, ImageCropApi,
    AllDocumentsApi
)


def routers(api_app):
    api_app.add_resource(TabularApi, "/api/tabular", endpoint="tabular-api")
    api_app.add_resource(TabularDeleteApi, "/api/tabular/<pk>", endpoint="tabular-delete-api")
    api_app.add_resource(TabularHead, "/api/tabular/<pk>/head", endpoint="tabular-get-head")
    api_app.add_resource(
        TabularSelect,
        "/api/tabular/<pk>/select/<column_name>",
        endpoint="tabular-select-column"
    )
    api_app.add_resource(
        TabularSelectWithQuery,
        "/api/tabular/<pk>/select/<column_name>/<operator>/<value>",
        endpoint="tabular-select-column-with_query"
    )
    api_app.add_resource(
        TabularInfo,
        "/api/tabular/<pk>/info",
        endpoint="tabular-file-info"
    )
    api_app.add_resource(
        TabularSelectWithComplexQuery,
        '/api/tabular/<pk>/select/<right_column_name>/<right_operator>/<right_value>/<operator>/<left_column_name>/<left_operator>/<left_value>',
        endpoint="tabular-select-complex-with_query"
    )
    api_app.add_resource(
        TabularMeanApi,
        "/api/tabular/<pk>/<column_name>/mean",
        endpoint="tabular-mean-column"
    )
    api_app.add_resource(
        TabularMedianApi,
        "/api/tabular/<pk>/<column_name>/median",
        endpoint="tabular-median-column"
    )
    api_app.add_resource(
        TabularModeApi,
        "/api/tabular/<pk>/<column_name>/mode",
        endpoint="tabular-mode-column"
    )
    api_app.add_resource(
        TabularQuantileApi,
        "/api/tabular/<pk>/<column_name>/quantile",
        endpoint="tabular-quantile"
    )
    api_app.add_resource(
        TabularUpdateDataSetApi,
        "/api/tabular/<pk>/<int:index>",
        endpoint="tabular-update-data-set"
    )

    # text analysis
    api_app.add_resource(
        TextKeywordExtraction,
        "/api/text/keyword_extraction"
    )
    api_app.add_resource(
        ClassificationApi,
        "/api/text/categorization"
    )
    api_app.add_resource(
        TextFullSearch,
        "/api/text/search"
    ),
    api_app.add_resource(
        AllDocumentsApi,
        "/api/text/all"
    )

    # image analysis
    api_app.add_resource(
        UploadImageApi,
        "/api/image/"
    )
    api_app.add_resource(
        ImageResizerApi,
        "/api/image/<pk>/resize"
    )
    api_app.add_resource(
        ImageCropApi,
        "/api/image/<pk>/crop"
    )
