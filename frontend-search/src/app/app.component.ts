import {Component, OnInit} from '@angular/core';
import {ElasticsearchService} from "./elasticsearchService";
import {FormControl} from "@angular/forms";
import {combineLatest, map, Observable, startWith, switchMap} from "rxjs";


@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrl: './app.component.css'
})
export class AppComponent implements OnInit{
  title = 'frontend-search';

  testSearch:string = "computer";
  constructor(private elasticsearchService:ElasticsearchService) {
  }

  pageNumber = 1;
  pageSize = 10;
  totalArticles = 0;

  selectedPage = 1;
  documents: any[] = [];

  searchControl = new FormControl("");
  filteredOptions!: Observable<string[]>;

   private _filter(value: string): Observable<string[]> {

     let lastElement = value.split(" ")[value.split(" ").length - 1];

    const queryString = JSON.stringify({
      query: {
        prefix: {
          'keyword': {
            value: lastElement
          }
        }
      },
      size: 10
    });

    return this.elasticsearchService.searchTopic(queryString).pipe(
      map((response: ElasticsearchResponse) => {
        return response.hits.hits.map(hit => hit._source.keyword);
      }),
      map(suggestedTopics => suggestedTopics.filter(keyword => keyword.toLowerCase().includes(lastElement.toLowerCase())))
    );
  }

   ngOnInit() {
    this.filteredOptions = this.searchControl.valueChanges.pipe(
      startWith(''),
      switchMap(value => this._filter(value || '')),
    );
  }

  searchFirstPage(){
      this.pageNumber = 1;
    this.testSearchMethod();
  }

  goToPage() {
    if(this.selectedPage > this.getTotalPages() || this.selectedPage < 1)
      return
    this.pageNumber = this.selectedPage;
    this.testSearchMethod();
  }

  getTotalPages(): number {
    return Math.ceil(this.totalArticles / this.pageSize);
  }

  testSearchMethod(){
     let topicName = this.searchControl.value as string;
     let keywords = topicName.split(" ");
     const shouldMatchQueries = keywords.map(keyword => ({
      match: { "topics.topic.keyword": keyword }
    }));

    const requestBody = {
      from: (this.pageNumber - 1) * this.pageSize,
      size: this.pageSize,
      query: {
        bool: {
          should: shouldMatchQueries,
          minimum_should_match: shouldMatchQueries.length
        }
      },
      sort: [
        {
          "topics.topic.keywordValue": {
            "order": "desc"
          }
        }
      ]
    };

    this.elasticsearchService.searchArticle(JSON.stringify(requestBody)).subscribe({
      next: (response:ElasticsearchResponse) => {
        this.totalArticles = response.hits.total.value
        this.documents = response.hits.hits.map(hit => hit._source);
      },
      error: () => {console.log("error")}
    });
  }

  getSearchInput(){
    let topicName = this.searchControl.value as string;
    let keywords = topicName.split(" ");
    const temp = keywords.slice(0, -1);
    temp.push("")
    let joinedString = temp.join(' ');
    return joinedString;
  }

}
