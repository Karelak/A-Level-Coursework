from src.meeting_room_manager import create_app

app = create_app()
if __name__ == "__main__":
    # flask will be run whenever this file gets executed directly so might as well use debug=true as flask is only used for development and testing
    app.run(debug=True, host="127.0.0.1", port=8001)
