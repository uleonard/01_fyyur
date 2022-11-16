#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
from tkinter.dnd import DndHandler
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
#from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
from models import db, Venue, Artist, Show
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
#db = SQLAlchemy(app)

# TODO: connect to a local postgresql database
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:Umali2022@localhost:5432/fyrr'
db.init_app(app)

migrate = Migrate(app, db)


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
  
  
  venues = Venue.query.order_by('city').all()


  data2 = []
  for venue in db.session.query(Venue.city,Venue.state).distinct().all():     
      venues = []
      for row in db.session.query(Venue).filter_by(city = venue.city):
        venues.append({"id":row.id,"name":row.name,"num_upcoming_shows":0})
      
      data2.append({
        "city":venue.city,
        "state":venue.state,
        "venues":venues
        })
    

  #return data2
  
  return render_template('pages/venues.html', areas=data2)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on venues with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  
  search = request.form.get('search_term', '')
  results = Venue.query.filter(Venue.name.ilike('%'+search+'%')).all()
  
  records = []
  for record in results:
    records.append({"id":record.id,"name":record.name,"num_upcoming_shows":0})

  response={
      "count": len(records),
      "data": records
    }


  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id

 # data = list(filter(lambda d: d['id'] == venue_id, [data1, data2, data3]))[0]

  venue = Venue.query.get(venue_id)

  #Please note that I have used join() only for past shows and I have not filtered date directly in the query
  #I realized that the start_time field was defined as string field and not as date in the Model
  #So I am filtering inside the loop for both upcoming and past events

  #Looking at the type of queries made, and the relationship defined in the models, I do not see
  #why joining was necessary for this action, as I see the relation is already doing something greate
  #as the second loop below for upcoming shows
  past_shows =  []
  for show in db.session.query(Show).join(Venue).filter(Show.venue_id==venue_id).all():
    date = dateutil.parser.parse(show.start_time)
    if date < datetime.now():
      past_shows. append( {
                    "artist_id": show.artist.id,
                    "artist_name": show.artist.name,
                    "artist_image_link": show.artist.image_link,
                    "start_time": show.start_time
                  }
                )
    
  upcoming_shows =  []
  for show in Show.query.filter_by(venue_id=venue_id):
    date = dateutil.parser.parse(show.start_time)
    if date > datetime.now():
      upcoming_shows. append( {
                    "artist_id": show.artist.id,
                    "artist_name": show.artist.name,
                    "artist_image_link": show.artist.image_link,
                    "start_time": show.start_time
                  }
                )   

  data={
    "id": venue.id,
    "name": venue.name,
    "genres": venue.genres.split(',') ,
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website_link,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talents,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count":len(past_shows),
    "upcoming_shows_count": len(upcoming_shows),
  }

 # data = list(filter(lambda d: d['id'] == venue_id, [data1, data2, data3]))[0]


  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion

  # on successful db insert, flash success
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/


  try:
    genres = ""
    for i in request.form.getlist('genres'):
      genres = genres + "," + i
    
    form = VenueForm(request.form)
    if form.validate_on_submit():
      venue = Venue(
              name = request.form['name'],
              city = request.form['city'],
              state = request.form['state'],
              address = request.form['address'],
              phone = request.form['phone'],
              genres = genres,
              image_link = request.form['image_link'],
              website_link = request.form['website_link'],
              facebook_link = request.form['facebook_link'],
              seeking_talents = request.form.get('seeking_talent','n'),
              seeking_description = request.form.get('seeking_description','')
      )
      #print(venue)
      
      db.session.add(venue)
      db.session.commit()
      flash('Venue ' + request.form['name'] + ' was successfully listed!')
    else:
      for field,message in form.errors.items():
        flash(field + '-' + str(message), 'danger')
  except:
    db.session.rollback()
    flash('An error occured: Venue ' + request.form['name'] + ' could not be listed!')
  finally:
    db.session.close()



  return render_template('pages/home.html')

@app.route('/venues/<venue_id>/delete', methods=['GET'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage

  try:
    Venue.query.filter_by(id = venue_id).delete()
    db.session.commit()
  except:
    db.session.rollback()
  finally:
    db.session.close()

  return redirect(url_for('index'))
  #return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
 
  data = []
  rows = Artist.query.all()
  for row in rows:
    data.append({"id":row.id, "name":row.name})
  
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
   
  search = request.form.get('search_term', '')
  results = Artist.query.filter(Artist.name.ilike('%'+search+'%')).all()
  
  records = []
  for record in results:
    records.append({"id":record.id,"name":record.name,"num_upcoming_shows":0})

  response={
      "count": len(records),
      "data": records
    }


  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
    
  artist = Artist.query.get(artist_id)

  
  #Please note that I have note used join() and I have not filtered date directly in the query
  #I realized that the start_time field was defined as string field and not as date in the Model
  #So I am filtering inside the loop for both upcoming and past events.
  #The line of code below fails.

  #past_shows_query = db.session.query(Show).join(Venue).filter(Show.artist_id==artist_id).filter(datetime.strptime(Show.start_time, '%y-%m-%d %H:%M:%S')<datetime.now()).all() 
  
 
  
  past_shows_query = Show.query.filter(Show.artist_id==artist_id).all()
  past_shows =  []
  for show in past_shows_query:
    date = dateutil.parser.parse(show.start_time)
    if date < datetime.now():
      past_shows. append( {
                    "venu_id": show.venue.id,
                    "venue_name": show.venue.name,
                    "venue_image_link": show.artist.image_link,
                    "start_time": show.start_time
                  }
                )
      
  #upcoming_shows_query = Show.query.filter(Show.artist_id==artist_id).filter(Show.start_time>datetime.now()).all()
  upcoming_shows_query = Show.query.filter(Show.artist_id==artist_id).all()
  upcoming_shows =  []
  for show in upcoming_shows_query:
    date = dateutil.parser.parse(show.start_time)
    if date > datetime.now():
      upcoming_shows. append( {
                    "venue_id": show.venue.id,
                    "venue_name": show.venue.name,
                    "venue_image_link": show.artist.image_link,
                    "start_time": show.start_time
                  }
                )
  genres = artist.genres.split(',') 

  data={
    "id": artist.id,
    "name": artist.name,
    "genres": genres,
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website_link,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "seeking_description": artist.seeking_description,
    "image_link": artist.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count":len(past_shows),
    "upcoming_shows_count": len(upcoming_shows),
  }

  
  
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  row = Artist.query.get(artist_id)
  artist={
    "id": row.id,
    "name": row.name,
    "genres": row.genres.split(','),
    "city": row.city,
    "state": row.state,
    "phone": row.phone,
    "website": row.website_link,
    "facebook_link": row.facebook_link,
    "seeking_venue": row.seeking_venue,
    "seeking_description": row.seeking_description,
    "image_link": row.image_link
  }
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  try:
   
    genres = ""
    for i in request.form.getlist('genres'):
      genres = genres + "," + i

    artist = Artist.query.get(artist_id)
    artist.name = request.form['name']
    artist.city = request.form['city']
    artist.state = request.form['state']
    artist.phone = request.form['phone']
    artist.genres = genres
    artist.image_link = request.form['image_link']
    artist.facebook_link = request.form['facebook_link']
    artist.seeking_venue = request.form.get('seeking_venue','n')
    artist.seeking_description = request.form.get('seeking_description','')
    
    db.session.commit()
  
  except:
    db.session.rollback()
  finally:
    db.session.close()


  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  row = Venue.query.get(venue_id)
  form = VenueForm()
  venue={
    "id": row.id,
    "name": row.name,
    "genres": row.genres.split(","),
    "address": row.address,
    "city": row.city,
    "state": row.state,
    "phone": row.phone,
    "website": row.website_link,
    "facebook_link": row.facebook_link,
    "seeking_talent": row.seeking_talents,
    "seeking_description": row.seeking_description,
    "image_link": row.image_link
  }


  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes

  try:
   
    genres = ""
    for i in request.form.getlist('genres'):
      genres = genres + "," + i
    
    venue = Venue.query.get(venue_id)
    venue.name = request.form['name']
    venue.city = request.form['city']
    venue.state = request.form['state']
    venue.phone = request.form['phone']
    venue.genres = genres
    venue.image_link = request.form['image_link']
    venue.website_link = request.form['website_link']
    venue.facebook_link = request.form['facebook_link']
    venue.seeking_venue = request.form.get('seeking_venue','n')
    venue.seeking_description = request.form.get('seeking_description','')
    
    db.session.commit()
  
  except:
    db.session.rollback()
  finally:
    db.session.close()

  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion

  # on successful db insert, flash success
  #flash('Artist ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')

  try:
   
    genres = ""
    for i in request.form.getlist('genres'):
      genres = genres + "," + i

    artist = Artist(
            name = request.form['name'],
            city = request.form['city'],
            state = request.form['state'],
            phone = request.form['phone'],
            genres = genres,
            image_link = request.form['image_link'],
            website_link = request.form['website_link'],
            facebook_link = request.form['facebook_link'],
            seeking_venue = request.form.get('seeking_venue','n'),
            seeking_description = request.form.get('seeking_description','')
    )
    
    db.session.add(artist)
    db.session.commit()
    flash('Artist ' + request.form['name'] + ' was successfully posted!')
  except:
    db.session.rollback()
    flash('An error occured: Artist ' + request.form['name'] + ' could not be posted!')
  finally:
    db.session.close()


  
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  data = []
  shows = Show.query.all()
  for show in shows:
    data.append({
          "venue_id": show.venue.id,
          "venue_name": show.venue.name,
          "artist_id": show.artist.id,
          "artist_name": show.artist.name,
          "artist_image_link": show.artist.image_link,
          "start_time": show.start_time
        })

  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead

  # on successful db insert, flash success
 # flash('Show was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  
  
  try:
   
    show = Show(
            artist_id = request.form['artist_id'],
            venue_id = request.form['venue_id'],
            start_time = request.form['start_time']
    )
    
    db.session.add(show)
    db.session.commit()
    flash('Show  was successfully posted!')
  except:
    db.session.rollback()
    flash('An error occured: Show could not be posted!')
  finally:
    db.session.close()
 
 
  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
