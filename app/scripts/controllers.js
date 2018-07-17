'use strict';

/* Controllers */

var site = window.location.origin;
var app = angular.module('ReleaseUI.controllers', ['ngStorage']);

app.controller('MainController', ['$scope','$http','$location','$log', '$sessionStorage',
  function($scope, $http, $location, $log, $sessionStorage) {

    // Set static variables
    $scope.numPerPage = 15;
    $scope.numRequested = 45;
    var getBranches = function () {
      $http({
          method: 'GET',
          url: site + '/branches',
          cache: true
      }).then(function successCallback(response) {
          $scope.branches = angular.fromJson(response.data);
      }, function errorCallback(response) {
          $log.log(response);
      });
    };
    getBranches();

    var getTypes = function () {
      $http({
          method: 'GET',
          url: site + '/types',
          cache: true
      }).then(function successCallback(response) {
          $scope.types = angular.fromJson(response.data);
      }, function errorCallback(response) {
          $log.log(response);
      });
    };
    getTypes();

    $scope.stateValues = [
      {"id":2, "status": "Finished"},
      {"id":3, "status": "Failed"},
      {"id":1, "status": "Pending"},
      {"id":4, "status": "Abandoned"},
    ];

    // Set default values for storage
    var defaultStorage = {
      stateValue: null,
      currentPage: 1,
      maxDate: new Date(),
      maxFromDate: new Date(),
      minToDate: new Date(0),
      fromDate: new Date(0),
      toDate: new Date(),
      startDate: null,
      endDate: null,
      whichDate: 'started',
      branchValue: null,
      typeValue: null,
      sortMethod: 3,
      releases: []
    };
    $scope.$storage = $sessionStorage.$default(defaultStorage);

    // Instantiates variables in scope based on stored information
    var setScope = function () {
      $scope.maxDate = new Date($scope.$storage.maxDate);
      $scope.maxFromDate = new Date($scope.$storage.maxFromDate);
      $scope.minToDate = new Date($scope.$storage.minToDate);
      $scope.fromDate = new Date($scope.$storage.fromDate);
      $scope.toDate = new Date($scope.$storage.toDate);
      $scope.filterDate = $scope.$storage.whichDate;

      if ($scope.$storage.startDate != null ) {
        $scope.startDate = new Date($scope.$storage.startDate);
      }
      if ($scope.$storage.endDate != null){
        $scope.endDate = new Date($scope.$storage.endDate);
      }

      $scope.selectedValue = $scope.$storage.stateValue;
      $scope.selectedBranch = $scope.$storage.branchValue;
      $scope.selectedType = $scope.$storage.typeValue;
    };

    // Set Scope when loading page
    setScope();

    // HTTP Request to get release information
    var getReleases = function (method) {

      var state;
      if($scope.$storage.stateValue == null) {
        state = 0;
      }
      else {
        state = $scope.$storage.stateValue;
      }

      var start = new Date($scope.$storage.fromDate);
      start = Math.floor(start.getTime() / 1000);
      var end = new Date($scope.$storage.toDate);
      end = Math.ceil(end.getTime() / 1000);

      var offset;
      if (method == 'page') {
        offset = $scope.$storage.releases.length;
      }
      else if (method == 'onload') {
        offset = 0;
      }
      else {
        offset = 0;
        $scope.$storage.currentPage = 1;
      }
      // put the sorting into an enum and bool based format, as opposed to a
      // stricly enum format
      var sortMethodDescending;
      if (($scope.$storage.sortMethod % 2) == 1) {
        sortMethodDescending = 1;
      } else {
        sortMethodDescending = 0;
      }
      var sortMethodNum;
      if ($scope.$storage.sortMethod <= 2) {
        sortMethodNum = 1;
      } else if ($scope.$storage.sortMethod <= 4) {
        sortMethodNum = 2;
      } else if ($scope.$storage.sortMethod <= 6) {
        sortMethodNum = 3;
      } else if ($scope.$storage.sortMethod <= 8) {
        sortMethodNum = 4;
      }

      var url_string = site + '/releases?state=' + state +
          '&branch=' + $scope.$storage.branchValue +
          '&release_type=' + $scope.$storage.typeValue + '&start_date=' + start +
          '&end_date=' + end + '&datetype=' + $scope.$storage.whichDate +
          '&sort_method='+ sortMethodNum + '&limit=' + $scope.numRequested +
          '&offset=' + offset + '&descending=' + sortMethodDescending;

      $http({
           method: 'GET',
           url: url_string,
           cache: false
       }).then(function successCallback(response) {
          var data = transform(response.data);
          if (method == 'page') {
            $scope.$storage.releases = $scope.$storage.releases.concat(data);
          }
          else {
            $scope.$storage.releases = data;
          }
           $scope.totalPages = Math.ceil($scope.$storage.releases.length / $scope.numPerPage);
           $log.log('request successful');
       }, function errorCallback(response) {
           $log.log(response);
       });
    };
    getReleases('onload');

    // onclick/onchange functions that may request more data from server
    $scope.dateChange = function (from, input) {
      if (from) {
        $scope.$storage.fromDate = input;
        $scope.$storage.minToDate = input;
        $scope.$storage.startDate = input;
      }
      else {
        $scope.$storage.toDate = input;
        $scope.$storage.maxFromDate = input;
        $scope.$storage.endDate = input;
      }
      setScope();
      getReleases('onDateChange');
    };

    $scope.dateTypeChange = function (input) {
      if (input == 0) {
        $scope.$storage.whichDate = 'started';
        $scope.$storage.sortMethod = 3;
      }
      else {
        $scope.$storage.whichDate = 'last_modified';
        $scope.$storage.sortMethod = 5;
      }
      setScope();
      getReleases('onDateTypeChange');
    };

    $scope.filterChange = function (type, input) {
      if (type == 0) {
        $scope.$storage.stateValue = input;
        $scope.$storage.selectedValue = input;
      }
      else if (type == 1) {
        $scope.$storage.branchValue = input;
        $scope.$storage.selectedBranch = input;
      }
      else {
        $scope.$storage.typeValue = input;
        $scope.$storage.selectedType = input;
      }
      setScope();
      getReleases('onFilterChange');
    };

    $scope.sortChange = function (input) {
      if ($scope.$storage.sortMethod % 2 == 0) {
        $scope.$storage.sortMethod = input;
      }
      else {
        $scope.$storage.sortMethod = input + 1;
      }
      getReleases('onSortChange');
    };

    $scope.pageChange = function (input) {
      if (input == -2) {
        $scope.$storage.currentPage = 1;
      }
      else if ($scope.$storage.currentPage + input < $scope.totalPages - 1){
        $scope.$storage.currentPage = $scope.$storage.currentPage + input;
      }
      else {
        getReleases('page');
        $scope.$storage.currentPage = $scope.$storage.currentPage + input;
      }
    };

    // Reset Filters and OrderBy
    $scope.resetFilter = function () {
      // Reset default settings and scope
      $sessionStorage.$reset(defaultStorage);
      setScope();

      // Reset dropdowns in UI
      $scope.defaultStatus = true;
      $scope.defaultBranch = true;
      $scope.defaultType = true;
      $scope.startDate = null;
      $scope.endDate = null;

      getReleases('onload');
    };

    // Redirect to Details function onclick of table row
    $scope.redirectToDetails = function (input) {
      var newRoute = '/' + input.release_id;
      $location.path(newRoute);
    };
}]);

app.controller('DetailsController', ['$scope', '$location', '$log', '$http', '$routeParams',
  function ($scope, $location, $log, $http, $routeParams) {

    var release_name = $routeParams.release_id;

    // Request release details
    $http({
         method: 'GET',
         url: site + '/release?release=' + release_name,
         cache: true
     }).then(function successCallback(response) {
         $scope.release = angular.fromJson(response.data);
     }, function errorCallback(response) {
         $log.log(response);
     });

    // Request task details
    $http({
         method: 'GET',
         url: site + '/tasks?release=' + release_name,
         cache: true
     }).then(function successCallback(response) {
          $scope.tasks = transform(response.data);
     }, function errorCallback(response) {
         $log.log(response);
     });
}]);

var transform =
  /**
  * Transforms json object to array
  * @param {Object} input
  * @return {Array}
  */
  function (input) {
  input = angular.fromJson(input);
  var output = [];

  angular.forEach(input, function(item) {
    output.push(item);
  });
   return output;
};
