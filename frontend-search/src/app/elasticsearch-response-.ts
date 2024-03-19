interface ElasticsearchResponse {
  hits: {
    total: any;
    hits: {
      _source: any;
    }[];
  };
}
