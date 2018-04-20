# https://www.programcreek.com/python/example/51515/flask.Response

## Create Flask Response of desird MIME

def scrape():
    """
    Scrape call.

    Ex: http://example.com/scrape.php?info_hash=aaaaaaaaaaaaaaaaaaaa&info_hash=bbbbbbbbbbbbbbbbbbbb&info_hash=cccccccccccccccccccc
    https://wiki.theory.org/BitTorrentSpecification#Tracker_.27scrape.27_Convention
    """

    files = {}
     # files: a dictionary containing one key/value pair for each torrent for which there are stats. If info_hash was supplied and was valid, this dictionary will contain a single key/value. Each key consists of a 20-byte binary info_hash. The value of each entry is another dictionary containing the following:
     #    complete: number of peers with the entire file, i.e. seeders (integer)
     #    downloaded: total number of times the tracker has registered a completion ("event=complete", i.e. a client finished downloading the torrent)
     #    incomplete: number of non-seeder peers, aka "leechers" (integer)
     #    name: (optional) the torrent's internal name, as specified by the "name" file in the info section of the .torrent file

    response = bencode({
        'files': files,
    })
    return Response(response, mimetype='text/plain') 


def format_exception(self, e, target, action):
        """
        Format the exception to a valid JSON object.

        Returns a Flask Response with the error.

        """
        exception_cls = e.__class__.__name__
        if self.error_status.get(exception_cls):
            status = self.error_status.get(exception_cls)
        else: # pragma: no cover
            status = 500
        if exception_cls in ('BadRequest', 'Forbidden','Unauthorized'):
            e.message = e.description
        error = dict(action=action.upper(),
                     status="failed",
                     status_code=status,
                     target=target,
                     exception_cls=exception_cls,
                     exception_msg=str(e.message))
        return Response(json.dumps(error), status=status,
                        mimetype='application/json') 


def export_to_csv(self, ids):
        qs = json.loads(self.model.objects(id__in=ids).to_json())

        def generate():
            yield ','.join(list(max(qs, key=lambda x: len(x)).keys())) + '\n'
            for item in qs:
                yield ','.join([str(i) for i in list(item.values())]) + '\n'

        return Response(
            generate(),
            mimetype="text/csv",
            headers={
                "Content-Disposition":
                "attachment;filename=%s.csv" % self.model.__name__.lower()
            }
        ) 


