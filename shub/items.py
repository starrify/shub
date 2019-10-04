from __future__ import absolute_import
import click

from shub.utils import job_resource_iter, get_job


HELP = """
Given a job ID, fetch items for that job from Scrapy Cloud and output them as
JSON lines.

A job ID consists of the Scrapinghub project ID, the numerical spider ID, and
the job ID, separated by forward slashes, e.g.:

    shub items 12345/2/15

You can also provide the Scrapinghub job URL instead:

    shub items https://app.scrapinghub.com/p/12345/2/15

You can omit the project ID if you have a default target defined in your
scrapinghub.yml:

    shub items 2/15

Or use any target defined in your scrapinghub.yml:

    shub items production/2/15

If the job is still running, you can watch the items as they are being scraped
by providing the -f flag:

    shub items -f 2/15

Additional filters may be applied to the query:

    shub items 12345/2/15 --filter '["foo","exists",[]]'
"""

SHORT_HELP = "Fetch items from Scrapy Cloud"


@click.command(help=HELP, short_help=SHORT_HELP)
@click.argument('job_id')
@click.option('-f', '--follow', help='output new items as they are scraped',
              is_flag=True)
@click.option('-n', '--tail', help='output last N items only', type=int)
@click.option('--filter', 'filter_', help='filter to be applied to the query')
@click.option('--filter_type', default='filter',
              type=click.Choice(['filter', 'filterall', 'filterany']),
              help='type of filter to be applied')
def cli(job_id, follow, tail, filter_, filter_type):
    job = get_job(job_id)
    for item in job_resource_iter(job, job.items, output_json=True,
                                  follow=follow, tail=tail, filter_=filter_,
                                  filter_type=filter_type):
        click.echo(item)
