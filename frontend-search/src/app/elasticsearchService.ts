import {HttpClient, HttpHeaders} from '@angular/common/http';
import { Injectable } from '@angular/core';
import {Observable} from "rxjs";

@Injectable({
  providedIn: 'root'
})
export class ElasticsearchService {

  constructor(private http: HttpClient) { } // Ensure HttpClient is injected here

  private esUrlArticle = 'http://localhost:9200/article/_search';
  private esUrlTopic = 'http://localhost:9200/keyword/_search';

  searchArticle(requestBody: any): Observable<any> {
    const headers = new HttpHeaders({
      'Content-Type': 'application/json'
    });

   return this.http.post<ElasticsearchResponse>(this.esUrlArticle, requestBody, { headers });
  }

  searchTopic(requestBody: any): Observable<any> {
    const headers = new HttpHeaders({
      'Content-Type': 'application/json'
    });

   return this.http.post<ElasticsearchResponse>(this.esUrlTopic, requestBody, { headers });
  }

}




