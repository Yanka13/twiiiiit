from flask_restx import Namespace, Resource, fields
from app.models import Tweet
from app import db

api = Namespace('tweets')  # Base route

json_tweet = api.model('Tweet', {
    'id': fields.Integer(required=True),
    'text': fields.String(required=True, min_length=1),
    'created_at': fields.DateTime(required=True),
})

json_new_tweet = api.model('New tweet', {
    # Don't allow empty string
    'text': fields.String(required=True, min_length=1),
})


@api.route('/<int:id>')  # route extension (ie: /tweets/<int:id>)
@api.response(404, 'Tweet not found')
@api.param('id', 'The tweet unique identifier')
class TweetResource(Resource):
    @api.marshal_with(json_tweet)
    def get(self, id):
        tweet = db.session.query(Tweet).get(id)
        if tweet is None:
            api.abort(404, "Tweet {} doesn't exist".format(id))
        else:
            return tweet

    @api.marshal_with(json_tweet, code=200)
    @api.expect(json_new_tweet, validate=True)
    def patch(self, id):
        tweet = db.session.query(Tweet).get(id)
        if tweet is None:
            api.abort(404, "Tweet {} doesn't exist".format(id))
        else:
            tweet.text = api.payload["text"]
            db.session.commit()
            return tweet

    def delete(self, id):
        tweet = db.session.query(Tweet).get(id)
        if tweet is None:
            api.abort(404, "Tweet {} doesn't exist".format(id))
        else:
            db.session.delete(tweet)
            db.session.commit()
            return None


@api.route('')
@api.response(422, 'Invalid tweet')
class TweetsResource(Resource):
    @api.marshal_with(json_tweet, code=201)
    @api.expect(json_new_tweet, validate=True)
    def post(self):
        text = api.payload["text"]
        if len(text) > 0:
            tweet = Tweet(text=text)
            db.session.add(tweet)
            db.session.commit()
            return tweet, 201
        else:
            return abort(422, "Tweet text can't be empty")

    @api.marshal_with(json_tweet)
    def get(self):
        return db.session.query(Tweet).all(), 201
