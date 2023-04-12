# e-IPO Scraper

A scraper based on Scrapy should be developed to extract all IDX IPO data from e-ipo.co.id.


## Run FlareSolverr Docker

```sh
docker run -d \
  --name=flaresolverr \
  -p 8191:8191 \
  -e LOG_LEVEL=info \
  --restart unless-stopped \
  ghcr.io/flaresolverr/flaresolverr:latest
```

