def handler(request):
    return {
        'status': 200,
        'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
        'body': '{"message": "API works!"}'
    }
