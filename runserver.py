import kluge_web

app, api = kluge_web.create_app()

if __name__ == '__main__':
    app.run(debug=True)