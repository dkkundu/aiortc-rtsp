from flask import Flask, render_template, Response
import cv2
import asyncio
from aiortc import RTCPeerConnection, VideoStreamTrack, RTCSessionDescription
from aiortc.contrib.media import MediaPlayer

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

class VideoTransformTrack(VideoStreamTrack):
    def __init__(self, track):
        super().__init__()
        self.track = track

    async def recv(self):
        frame = await self.track.recv()
        return frame

async def run(pc, player):
    pc.addTrack(player.audio)
    pc.addTrack(VideoTransformTrack(player.video))
    await pc.setLocalDescription(await pc.createOffer())

@app.route('/video_feed')
def video_feed():
    cap = cv2.VideoCapture("rtsp://your_rtsp_stream_url")
    player = MediaPlayer("rtsp://your_rtsp_stream_url")
    pc = RTCPeerConnection()
    asyncio.run(run(pc, player))
    return Response(gen_frames(pc),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

def gen_frames(pc):
    while True:
        frame = asyncio.run(get_frame(pc))
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

async def get_frame(pc):
    frame = await VideoTransformTrack.recv(pc)
    return cv2.imencode('.jpg', frame)[1].tobytes()

if __name__ == '__main__':
    app.run(debug=True)
