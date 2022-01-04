import logging

from moto.sns import sns_backends as moto_sns_backends
from moto.sns.exceptions import SNSNotFoundError
from moto.sns.models import SNSBackend as MotoSNSBackend

from localstack.aws.api import RequestContext
from localstack.aws.api.sns import NotFoundException, SnsApi
from localstack.services.sns.sns_listener import SNSBackend

LOG = logging.getLogger(__name__)


def get_backend(context: RequestContext) -> SNSBackend:
    return SNSBackend.get(context.region)


def get_moto_backend(context: RequestContext) -> MotoSNSBackend:
    return moto_sns_backends[context.region]


class SnsProvider(SnsApi):
    def delete_topic(self, context: RequestContext, topic_arn: str) -> None:
        LOG.debug("deleting topic %s", topic_arn)

        # delete data from moto backend
        try:
            get_moto_backend(context).delete_topic(topic_arn)
        except SNSNotFoundError as e:
            raise NotFoundException(e.message)

        # delete data that localstack keeps on top of moto data
        sns_backend = get_backend(context)
        sns_backend.sns_subscriptions.pop(topic_arn, None)
        sns_backend.sns_tags.pop(topic_arn, None)
