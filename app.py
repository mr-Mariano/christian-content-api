import falcon
from db.mongo import init_indexes
from db.dgraph import init_schema

from routes.auth import RegisterResource, LoginResource, LogoutResource
from routes.user import (
    UpdateUserResource, AddPreferenceResource,
    RemovePreferenceResource, ListUsersResource
)
from routes.content import (
    ContentResource, RecommendContentResource,
    ContentMetricsResource, TrendingContentResource
)
from routes.like import LikeResource
from routes.comment import CommentResource, GetCommentsResource, GetCommentsByUserResource
from routes.share import ShareResource, ShareExternalResource
from routes.notes import NotesResource, UpdateNoteResource, DeleteNoteResource
from routes.follow import FollowResource, RecommendUsersResource, RecommendByLocationResource
from routes.events import (
    EventResource, EventsByLocationResource,
    AttendEventResource, UserEventsResource,
    RecommendEventsByConnectionsResource
)
from routes.stats import (
    ActivityResource, ActivityFilteredResource,
    DailyActiveUsersResource, ContentActivityResource,
    SystemStatsResource
)
from routes.search import SemanticSearchResource
from routes.chatbot import ChatbotResource, ConversationsResource
from routes.admin import ResetResource


init_indexes()
init_schema()

app = falcon.App()

# auth
app.add_route('/register', RegisterResource())
app.add_route('/login', LoginResource())
app.add_route('/logout', LogoutResource())

# user
app.add_route('/user/update', UpdateUserResource())
app.add_route('/user/add-preference', AddPreferenceResource())
app.add_route('/user/remove-preference', RemovePreferenceResource())
app.add_route('/users', ListUsersResource())

# content
app.add_route('/content', ContentResource())
app.add_route('/recommend/content/{user_id}', RecommendContentResource())
app.add_route('/metrics/content', ContentMetricsResource())
app.add_route('/metrics/content/{content_id}', ContentActivityResource())
app.add_route('/trending', TrendingContentResource())

# likes / comments / shares
app.add_route('/like', LikeResource())
app.add_route('/comment', CommentResource())
app.add_route('/comments/{content_id}', GetCommentsResource())
app.add_route('/comments/user/{user_id}', GetCommentsByUserResource())
app.add_route('/share', ShareResource())
app.add_route('/share-external', ShareExternalResource())

# notes
app.add_route('/notes', NotesResource())
app.add_route('/notes/{user_id}', NotesResource())
app.add_route('/notes/update', UpdateNoteResource())
app.add_route('/notes/delete/{note_id}', DeleteNoteResource())

# follow
app.add_route('/follow', FollowResource())
app.add_route('/recommend/users/{user_id}', RecommendUsersResource())
app.add_route('/recommend/location/{user_id}', RecommendByLocationResource())

# events
app.add_route('/event', EventResource())
app.add_route('/events', EventsByLocationResource())
app.add_route('/attend-event', AttendEventResource())
app.add_route('/my-events/{user_id}', UserEventsResource())
app.add_route('/recommend/events/{user_id}', RecommendEventsByConnectionsResource())

# stats
app.add_route('/activity/{user_id}', ActivityResource())
app.add_route('/activity-filter/{user_id}', ActivityFilteredResource())
app.add_route('/dau', DailyActiveUsersResource())
app.add_route('/system-stats', SystemStatsResource())

# search / chatbot
app.add_route('/search-content', SemanticSearchResource())
app.add_route('/chatbot', ChatbotResource())
app.add_route('/conversations/{user_id}', ConversationsResource())

# admin
app.add_route('/reset', ResetResource())
