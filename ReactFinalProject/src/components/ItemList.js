import React from 'react';
import './ItemList.scss';

const ItemList = ({ items }) => {
    return (
        <div className="item-list">
            {items.map((item) => (
                <div className="item" key={item.key}>
                    <img
                        src={`http://covers.openlibrary.org/b/id/${item.cover_i}-L.jpg`}
                        alt={item.title}
                    />
                    <h3>{item.title}</h3>
                    <p><strong>Author:</strong> {item.author_name && item.author_name.join(', ')}</p>
                    <p><strong>First Published:</strong> {item.first_publish_year}</p>
                </div>
            ))}
        </div>
    );
};

export default ItemList;