#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import sys
import dateutil.parser
import babel.dates 
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
import config
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')


# TODO: connect to a local postgresql database
app.config['SQLALCHEMY_DATABASE_URI'] = config.SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app,db)
#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String , nullable=False)
    city = db.Column(db.String(120) , nullable=False)
    state = db.Column(db.String(120) , nullable=False)
    address = db.Column(db.String(120 ), nullable=False)
    phone = db.Column(db.String(120) ,  nullable=False)
    image_link = db.Column(db.String())
    facebook_link = db.Column(db.String(120))
      
    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    website_link = db.Column(db.String(120))
    genres = db.Column("genres" , db.ARRAY(db.String()) , nullable=False)
    seeking_talent = db.Column(db.Boolean , default=False)
    seeking_description = db.Column(db.String(200))
    shows = db.relationship('Show', backref='venue' )

    def __ref__(self):
      return f"Venue {self.id} name: {self.name}"

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String , nullable=False)
    city = db.Column(db.String(120)  , nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    genres = db.Column("genres" , db.ARRAY(db.String()), nullable=False)
    image_link = db.Column(db.String())
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(120))
    seeking_description = db.Column(db.String(200))
    looking_for_venues = db.Column(db.Boolean , default=False)
    shows = db.relationship('Show', backref='artist' )
    # TODO: implement any missing fields, as a database migration using Flask-Migrate
  
    def __ref__(self):
      return f"Artist {self.id} name: {self.name}"
    


# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

class Show(db.Model):

  __tablename__ = 'Show'

  id = db.Column(db.Integer, primary_key=True)
  artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id') , nullable=False)
  venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False )
  start_time = db.Column(db.DateTime , nullable=False)

  def __ref__(self):
      return f"Show {self.id} Artist: {self.artist_id} Venue:  {self.venue_id}"

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
  #venues = Venue.query.all() 
  

  data =[]
  #get all the venues
  venues = Venue.query.all()

  #using a set to avoid duplicates
  locations = set()

  for v in venues:
    #add both city and state to locations
    locations.add((v.city ,  v.state))
  
  #assigning the venues for each unique city_state
  for location in locations:
    data.append({"city": location[0], "state": location[1], "venues": [] })

  for venue in venues:
    num_upcoming_shows = 0
    #get the shows associated to the upcoming show
    shows = Show.query.filter_by(venue_id=venue.id).all()

    for show in shows:
      #condition to check if the show start_time is upcoming 
      if show.start_time > datetime.now():
        num_upcoming_shows += 1

    for venue_location in data:
      if venue.state == venue_location['state'] and venue.city == venue_location['city']:
        venue_location['venues'].append({
          "id" : venue.id,
          "name" : venue.name,
          "num_upcoming_shows" : num_upcoming_shows
        })

  
  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search_term = request.form.get('search_term')
  results = Venue.query.filter(Venue.name.ilike(f'%{search_term}%')).all()
  
  response={
    "count": len(results),
    "data": results
    
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  venue = Venue.query.get(venue_id)
  shows = Show.query.filter_by(venue_id = venue.id).all()
  past_shows = []
  upcoming_shows = []

  for show in shows:
    data = {
      "artist_id" : show.artist_id,
      "artist_name" : show.artist.name,
      "artist_image_link": show.artist.image_link,
      "start_time" : str(show.start_time),
    }

    if show.start_time  > datetime.now():
      upcoming_shows.append(data)
    else:
      past_shows.append(data)


  data = {
    "id":venue.id,
    "name": venue.name,
    "genres": venue.genres,
    "address" : venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website_link,
    "facebook_link" : venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link,
    "past_shows":  past_shows,
    "upcoming_shows" : upcoming_shows,
    "past_show_count": len(past_shows), 
    "upcoming_shows_count": len(upcoming_shows),

  }

  #data = list(filter(lambda d: d['id'] == venue_id, [data1, data2, data3]))[0]
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
    error = False 
    form = VenueForm()
    try:
     

      name =request.form.get('name')
      city = request.form.get('city')
      state  = request.form.get('state')
      address = request.form.get('address')
      phone = request.form.get('phone')
      image_link = request.form.get('image_link')
      genres = request.form.get('genres')
      facebook_link = request.form.get('facebook_link')
      website_link = request.form.get('website_link')
      seeking_talent = form.seeking_talent.data
    
      seeking_description = request.form.get('seeking_description')

      venue = Venue(name=name , city = city , state = state , address = address ,phone = phone, image_link = image_link ,seeking_talent=seeking_talent, genres = genres , facebook_link = facebook_link ,website_link = website_link ,seeking_description = seeking_description)
      db.session.add(venue)
      db.session.commit()
      
    

    except:
      error = True
      db.session.rollback()
      print(sys.exc_info())
    finally:
      db.session.close()
    if error:
      flash('Venue ' + request.form['name'] + ' was not successfully listed!')
      form = VenueForm()
      return render_template('forms/new_venue.html', form=form)
    else:
      flash('Venue ' + request.form['name'] + ' was successfully listed!')
      return render_template('pages/home.html')

  # TODO: modify data to be the data object returned from db insertion

  # on successful db insert, flash success
  
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  error = False
  try:

    venue = Venue.query.get(venue_id)
    venue_name = venue.name

    db.session.delete(venue)
    db.session.commit()
  except : 
    error = True 
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
      flash('Venue ' + venue_name + ' was not successfully deleted!')
      return redirect(url_for('index'))
  else:
    flash('Venue ' + venue_name + ' was not successfully deleted!')
    return redirect(url_for('index'))
  
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  data = []
  artists = Artist.query.all()
  for artist in artists:
    data.append({
      "id": artist.id,
      "name": artist.name
    })
  
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search_term = request.form.get('search_term','')
  
  result = Artist.query.filter(Artist.name.ilike(f'%{search_term}%')).all()

 
  response={
    "count": len(result),
    "data": result
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  artist = Artist.query.get(artist_id)
  shows = Show.query.filter_by(artist_id = artist.id).all()
  past_shows = []
  upcoming_shows = []

  for show in shows:
    data = {
      "venue_id" : show.venue_id,
      "venue_name" : show.venue.name,
      "venue_image_link": show.venue.image_link,
      "start_time" : str(show.start_time),
    }

    if show.start_time  > datetime.now():
      upcoming_shows.append(data)
    else:
      past_shows.append(data)


  data = {
    "id":artist.id,
    "name": artist.name,
    "genres": artist.genres,
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website_link,
    "facebook_link" : artist.facebook_link,
    "seeking_venue": artist.looking_for_venues,
    "seeking_description": artist.seeking_description,
    "image_link": artist.image_link,
    "past_shows":  past_shows,
    "upcoming_shows" : upcoming_shows,
    "past_show_count": len(past_shows), 
    "upcoming_shows_count": len(upcoming_shows),

  }

  
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.get(artist_id)
 
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):

    artist = Artist.query.get(artist_id)
    form = ArtistForm()
    error = False 
    
    try:
     

      artist.name =request.form.get('name')
      artist.city = request.form.get('city')
      artist.state  = request.form.get('state')
      artist.genres = request.form.get('genres')
      artist.phone = request.form.get('phone')
      artist.image_link = request.form.get('image_link')
      
      artist.facebook_link = request.form.get('facebook_link')
      artist.website_link = request.form.get('website_link')
      artist.looking_for_venues = form.seeking_venue.data
      artist.seeking_description = request.form.get('seeking_description')

      db.session.commit()    
      flash('Artist ' + artist.name + ' was successfully updated!')
      return redirect(url_for('show_artist', artist_id=artist_id))
    except:
      
      db.session.rollback()
      flash('Artist ' + artist.name + ' was successfully updated!')
      print(sys.exc_info())
      return render_template('forms/edit_artist.html', form=form, artist=artist)
    finally:
      db.session.close()


      
   
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.get(venue_id)

  
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
    venue = Venue.query.get(venue_id)
    error = False 
    form = VenueForm()
    try:
     
      venue.name =request.form.get('name')
      venue.city = request.form.get('city')
      venue.state  = request.form.get('state')
      venue.address = request.form.get('address')
      venue.phone = request.form.get('phone')
      venue.image_link = request.form.get('image_link')
      venue.genres = request.form.get('genres')
      venue.facebook_link = request.form.get('facebook_link')
      venue.website_link = request.form.get('website_link')
      
      venue.seeking_talent = request.form.get("seeking_talent")
      venue.seeking_description = request.form.get('seeking_description')

      db.session.commit()
      
    

    except:
      error = True
      db.session.rollback()
      print(sys.exc_info())
    finally:
      db.session.close()
    if error:
      flash('Venue ' + request.form['name'] + ' was not successfully updated!')
      return render_template('forms/edit_venue.html', form=form, venue=venue)
     
    else:
      flash('Venue ' + request.form['name'] + ' was successfully updated!')
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
    error = False 
    form = ArtistForm()
    try:
     

      name =request.form.get('name')
      city = request.form.get('city')
      state  = request.form.get('state')
      genres = request.form.get('genres')
      phone = request.form.get('phone')
      image_link = request.form.get('image_link')
      
      facebook_link = request.form.get('facebook_link')
      website_link = request.form.get('website_link')
      looking_for_venues = form.seeking_venue.data
      seeking_description = request.form.get('seeking_description')

      venue = Artist(name=name , city = city , state = state  ,phone = phone, image_link = image_link ,looking_for_venues=looking_for_venues, genres = genres , facebook_link = facebook_link ,website_link = website_link ,seeking_description = seeking_description)
      db.session.add(venue)
      db.session.commit()
      
    

    except:
      error = True
      db.session.rollback()
      print(sys.exc_info())
    finally:
      db.session.close()

    if error:
      flash('Artist ' + request.form['name'] + ' was not successfully listed!')
      form = VenueForm()
      return render_template('forms/new_venue.html', form=form)
    else:
      flash('Artist ' + request.form['name'] + ' was successfully listed!')
      return render_template('pages/home.html')
  


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.

  shows = Show.query.order_by(db.desc(Show.start_time)).all()

  data = []

  for show in shows:
    data.append({
    "venue_id" : show.venue_id,
    "venue_name" : show.venue.name,
    "artist_id" : show.artist_id,
    "artist_name" : show.artist.name,
    "artist_image_link": show.artist.image_link,
    "start_time": str(show.start_time)
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
  try:
    artist_id = request.form.get("artist_id")
    venue_id = request.form.get("venue_id")
    start_time = request.form.get("start_time")

    show = Show(artist_id=artist_id, venue_id=venue_id , start_time=start_time)
    db.session.add(show)
    db.session.commit()
    flash('Show was successfully listed!')
  # on successful db insert, flash success
  except:
     db.session.rollback()
     flash('Show was not successfully listed!')
  finally:
     db.session.close()
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
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
