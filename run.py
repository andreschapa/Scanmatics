##from views import app original one
from project import app
import os
app.run(debug=True) #use this when testing and deploying locally

#port = int(os.environ.get('PORT', 5000)) ##for running on heroku
#app.run(host='0.0.0.0', port=port) ##for running on heroku