# app.secret_key = 'xxcc3344'

# if __name__ == '__main__':
#     app.run(debug=True, port=5000)


from image_restorer import create_app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True, port=5000)
