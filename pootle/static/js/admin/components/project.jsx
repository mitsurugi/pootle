/*
 * Copyright (C) Pootle contributors.
 *
 * This file is a part of the Pootle project. It is distributed under the GPL3
 * or later license. See the LICENSE file for a copy of the license and the
 * AUTHORS file for copyright and authorship information.
 */

'use strict';

import React from 'react';

import { Project, ProjectSet } from 'models/project';
import ProjectForm from './ProjectForm';
import Search from './Search';


let ProjectsAdmin = React.createClass({

  propTypes: {
    onAdd: React.PropTypes.func.isRequired,
    onCancel: React.PropTypes.func.isRequired,
    onDelete: React.PropTypes.func.isRequired,
    onSearch: React.PropTypes.func.isRequired,
    onSelectItem: React.PropTypes.func.isRequired,
    onSuccess: React.PropTypes.func.isRequired,
    searchQuery: React.PropTypes.string.isRequired,
    selectedItem: React.PropTypes.object,
  },

  render() {
    let viewsMap = {
      add: <ProjectAdd
              model={this.props.model}
              collection={this.props.items}
              onSuccess={this.props.onSuccess}
              onCancel={this.props.onCancel} />,
      edit: <ProjectEdit
              model={this.props.selectedItem}
              collection={this.props.items}
              onAdd={this.props.onAdd}
              onSuccess={this.props.onSuccess}
              onDelete={this.props.onDelete} />
    };

    let args = {
      count: this.props.items.count,
    };
    let msg;

    if (this.props.searchQuery) {
      msg = ngettext('%(count)s project matches your query.',
                     '%(count)s projects match your query.', args.count);
    } else {
      msg = ngettext(
        'There is %(count)s project.',
        'There are %(count)s projects. Below are the most recently added ones.',
        args.count
      );
    }
    let resultsCaption = interpolate(msg, args, true);

    let fields = ['index', 'code', 'fullname', 'disabled'];

    return (
      <div className="admin-app-projects">
        <div className="module first">
          <Search
            fields={fields}
            onSearch={this.props.onSearch}
            onSelectItem={this.props.onSelectItem}
            items={this.props.items}
            selectedItem={this.props.selectedItem}
            searchLabel={gettext('Search Projects')}
            searchPlaceholder={gettext('Find project by name, code')}
            resultsCaption={resultsCaption}
            searchQuery={this.props.searchQuery} />
        </div>

        <div className="module admin-content">
          {viewsMap[this.props.view]}
        </div>
      </div>
    );
  }

});


let ProjectAdd = React.createClass({

  propTypes: {
    onCancel: React.PropTypes.func.isRequired,
    onSuccess: React.PropTypes.func.isRequired,
  },

  /* Layout */

  render() {
    return (
      <div className="item-add">
        <div className="hd">
          <h2>{gettext('Add Project')}</h2>
          <button
            onClick={this.props.onCancel}
            className="btn btn-primary">{gettext('Cancel')}</button>
        </div>
        <div className="bd">
          <ProjectForm
            model={new this.props.model()}
            collection={this.props.collection}
            onSuccess={this.props.onSuccess} />
        </div>
      </div>
    );
  }

});


let ProjectEdit = React.createClass({

  propTypes: {
    onAdd: React.PropTypes.func.isRequired,
    onDelete: React.PropTypes.func.isRequired,
    onSuccess: React.PropTypes.func.isRequired,
  },

  /* Layout */

  render() {
    return (
      <div className="item-edit">
        <div className="hd">
          <h2>{gettext('Edit Project')}</h2>
          <button
            onClick={this.props.onAdd}
            className="btn btn-primary">{gettext('Add Project')}</button>
        </div>
        <div className="bd">
        {!this.props.model ?
          <p>{gettext('Use the search form to find the project, then click on a project to edit.')}</p> :
          <ProjectForm
            key={this.props.model.id}
            model={this.props.model}
            collection={this.props.collection}
            onSuccess={this.props.onSuccess}
            onDelete={this.props.onDelete} />
        }
        </div>
      </div>
    );
  }

});


export {
  ProjectsAdmin as App,
  Project as model,
  ProjectSet as collection,
};
