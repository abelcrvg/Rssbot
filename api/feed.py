def handler(request):
    try:
        with open("feed.xml", "r", encoding="utf-8") as f:
            data = f.read()

        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/rss+xml"
            },
            "body": data
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": str(e)
        }
