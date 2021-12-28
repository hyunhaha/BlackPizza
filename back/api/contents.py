from flask import Flask, jsonify, Blueprint, request, session
from numpy.random.mtrand import randint
from scipy.sparse.construct import random
from models import User, Contents, Genre, Actor, Buy, Streaming, Rent, User_Taste
from db_connect import db
from datateam.Recommendation import recommendations

contents = Blueprint('contents', __name__, url_prefix='/api/contents')


@contents.route('/list', methods=['GET'])
def list():
    if request.method == "GET":
        list_page = int(request.args.get('page'))
        movie_list = {'page': list_page, 'list': []}
        contents = Contents.query.order_by(Contents.open_year.desc()).all()[
            (list_page-1)*100+1:(list_page)*100]
        for content in contents:
            movie_dict = {}
            movie_dict['key'] = content.id
            movie_dict['info'] = [content.title, content.image]
            movie_list['list'].append(movie_dict)

    return jsonify(movie_list)


@contents.route('/recommend', methods=['GET', 'POST'])
def recommend():
    if request.method == 'POST':
        params = request.get_json()
        user_pick_list = params['data']
        user_pick_id = [i['contents_id'] for i in user_pick_list]
        user_scores = [i['score'] for i in user_pick_list]
        if session.get('email'):
            user_email = session['email']
            user_id = User.query.filter(User.email == user_email).first()['id']
            for taste in user_pick_list:
                new_taste = User_Taste(
                    user_id = user_id,
                    contents_id = taste['contents_id'], 
                    score = taste['score'] if 'score' in taste else None,
                    is_picked = taste['is_picked'] if 'is_picked' in taste else False
                )
                db.session.add(new_taste)
            db.session.commit()

    else:
        user_pick_id = random.sample([i for i in range(1, 100)], 10)
        user_scores = [randint(1, 10) for _ in range(10)]
    con_list = Contents.query.filter(Contents.id.in_(user_pick_id))
    user_pick = [i.title for i in con_list]

    contents_all = db.session.query(
        Contents.id, Contents.title, Contents.score, Contents.director).all()
    actors = db.session.query(Actor.contents_id, Actor.actor).all()
    genre = db.session.query(Genre.contents_id, Genre.genre).all()

    rcm_df = recommendations(user_pick, contents_all, actors, genre)

    # rcm -> response
    rcm_title = [line['제목'] for i, line in rcm_df.iterrows()]
    rcm_list = Contents.query.filter(Contents.title.in_(rcm_title))
    res = []
    content = {}
    for i in rcm_list:
        ott_info = {}
        content[i.id] = [i.title, i.image, ott_info]
        streaming_list = Streaming.query.filter(Streaming.contents_id == i.id)
        buy_list = Buy.query.filter(Buy.contents_id == i.id)
        rent_list = Rent.query.filter(Rent.contents_id == i.id)
        ott_info['streaming'] = [
            {'ott': i.ott, 'price': i.price, 'quality': i.quality} for i in streaming_list]
        ott_info['buy'] = [{'ott': i.ott, 'price': i.price,
                            'quality': i.quality} for i in buy_list]
        ott_info['rent'] = [{'ott': i.ott, 'price': i.price,
                            'quality': i.quality} for i in rent_list]

    ott_count = {}
    for value in content.values():
        otts = value[2]
        for key in otts.keys():
            for ott_dict in otts[key]:
                if ott_dict['ott'] in ott_count:
                    ott_count[ott_dict['ott']] += 1
                else:
                    ott_count[ott_dict['ott']] = 0

    res.append(content)
    res.append(ott_count)
    # print(res)
    return jsonify(res)


@contents.route('/detail/<id>', methods=['GET'])
def detail(id):
    if request.method == "GET":
        # content = detail_temp_list[id]
        content_detail = {}
        content = Contents.query.filter(Contents.id == id).first()
        genres = Genre.query.filter(Genre.contents_id == id).all()
        content_detail['genre'] = []
        for genre in genres:
            content_detail['genre'].append(genre.genre)
        actors = Actor.query.filter(Actor.contents_id == id).all()
        content_detail['actor'] = []
        for actor in actors:
            content_detail['actor'].append(actor.actor)
        content_detail['title'] = content.title
        content_detail['image'] = content.image
        content_detail['open_year'] = content.open_year
        content_detail['runtime'] = content.runtime.strftime("%H:%M")
        content_detail['director'] = content.director

    return jsonify(content_detail)


@contents.route('/test', methods=['GET', 'POST'])
def test():
    recommend_contents = db.session.query(Contents).all()
    res = {}
    for i in recommend_contents:
        content_info = []
        content_info.append(i.title)
        content_info.append(i.image)
        res[i.title] = content_info
    return jsonify(res)
