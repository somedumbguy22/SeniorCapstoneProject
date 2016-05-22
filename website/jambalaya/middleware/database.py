from jambalaya.settings import Session


class SQLAlchemySessionMiddleware(object):
    """
    Automatically manage a database session for each request.
    Handles opening the request, committing, and rollback in case of exception.
    From http://stackoverflow.com/a/6607461/221061
    """
    def process_request(self, request):
        request.db_session = Session()

    def process_response(self, request, response):
        try:
            session = request.db_session
        except AttributeError:
            return response
        try:
            session.commit()
            return response
        except:
            session.rollback()
            raise

    def process_exception(self, request, exception):
        try:
            session = request.db_session
        except AttributeError:
            return
        session.rollback()